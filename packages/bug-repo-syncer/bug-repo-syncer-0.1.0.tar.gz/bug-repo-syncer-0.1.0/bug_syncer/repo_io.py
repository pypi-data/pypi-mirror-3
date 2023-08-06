# -*- coding: utf-8 -*-
###############################################################################
#    Bug Repo Syncer - A program to synchronize bug repositories.             #
#                                                                             #
#    Copyright (C) 2012 by Eike Welk                                          #
#    eike.welk@gmx.net                                                        #
#                                                                             #
#    License: GPL V3                                                          #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
###############################################################################
"""
Communicate with the repositories
"""

from __future__ import division
from __future__ import absolute_import              

from xmlrpclib import ServerProxy, MultiCall, ProtocolError, ResponseError
from urlparse import urlparse
from getpass import getpass
from datetime import datetime
import time
import copy
from xml.parsers.expat import ExpatError
from launchpadlib.launchpad import Launchpad

from bug_syncer.common import TracData, LaunchpadData, DummyRepoData, BugData, \
    UserFatalError, UnknownRepoError, UnknownWordError, \
    EquivalenceTranslatorBase, EquivalenceTranslatorNoop



def safe_unicode(text):
    """Convert input to unicode, accepts str or unicode"""
    if isinstance(text, unicode):
        return text
    elif isinstance(text, str):
        return unicode(text, encoding="utf8", errors="replace")
    else:
        raise TypeError("Argument ``text`` must be of type ``str`` or "
                        "``unicode``. I got: " + str(type(text)))
        
        
        
class RepoController(object):
    """Base class of objects that control bug repositories.""" 
    def __init__(self):
        self.repo_name = "--undefined--"
        self.people_translator = EquivalenceTranslatorNoop()
        self.milestone_translator = EquivalenceTranslatorNoop()

    def get_recent_changes(self, time_since): 
        """Return list of bugs that changed since a certain date and time."""
        raise NotImplementedError()

    def get_bugs(self, bug_ids):
        """Get specified bugs from the server. Return list of bugs."""
        raise NotImplementedError()

    def update_bugs(self, bugs):
        """
        Change bugs, so that they have they same contents as the internal form.
        """
        raise NotImplementedError()
    
    def create_bugs(self, bugs):
        """
        Create new bugs in the remote repository. Returns: list[bug_id]
        """
        raise NotImplementedError()
    
    def delete_bugs(self, bug_ids):
        """Delete several bugs at once."""
        raise NotImplementedError()
    
    def people_intl2repo(self, name):
        """
        Translate name of people from internal to repository vocabulary.
        """
        if name is None or name == "*":
            return name
        else:
            return self.people_translator.intl2repo(self.repo_name, name)
    
    def people_repo2intl(self, name):
        """
        Translate name of people from repository to internal vocabulary.
        """
        if name is None:
            return None
        try:
            return self.people_translator.repo2intl(self.repo_name, name)
        except UnknownWordError:
            print "Warning! Unknown person: '{p}'".format(p=name)
            return "*"
    
    def milestone_intl2repo(self, ms_name):
        """
        Translate name of milestone from internal to repository vocabulary.
        """
        if ms_name is None or ms_name == "*":
            return ms_name
        else:
            return self.milestone_translator.intl2repo(self.repo_name, ms_name)
    
    def milestone_repo2intl(self, ms_name):
        """
        Translate name of milestone from repository to internal vocabulary.
        """
        if ms_name is None:
            return None
        try:
            return self.milestone_translator.repo2intl(self.repo_name, ms_name)
        except UnknownWordError:
            print "Warning! Unknown milestone: '{m}'".format(m=ms_name)
            return "*"

    

class RepoControllerDummy(RepoController):
    """
    Controller for testing.
    
    Does not connect to the Internet, but stores bugs internally
    """
    #pylint: disable=W0212
    def __init__(self, repo_data): #IGNORE:W0102
        RepoController.__init__(self)
        assert isinstance(repo_data, DummyRepoData)
        
        #RepoController protocol
        self.repo_name = repo_data.repo_name
        self.people_translator = EquivalenceTranslatorNoop()
        self.milestone_translator = EquivalenceTranslatorNoop()
        
        #Numbers of bugs read/written/created
        self.num_read = 0
        self.num_updated = 0
        self.num_created = 0
        #Internal bug storage
        self.bugs = {}
        
        if repo_data.initial_bugs:
            self.create_bugs(repo_data.initial_bugs)
            self.num_created = 0
            print "RepoControllerDummy.__init__: resetting counters after " \
                  "creating initial bugs."


    def get_recent_changes(self, time_since): 
        """
        Return list of bugs that changed since a certain date and time.
        """
        print "Repo '{n}': return changes since {t}." \
              .format(n=self.repo_name, t=time_since)   
        
        ret_bugs = []
        for bug in self.bugs.values():
            if bug.time_modified >= time_since:
                bug = copy.deepcopy(bug) #there might be mutable attributes
                ret_bugs.append(bug)
        
        self.num_read += len(ret_bugs)
        return ret_bugs
    

    def get_bugs(self, bug_ids):
        """Get specified bugs from the server. Return list of bugs."""
        print "Repo '{n}': received {i} bug IDs for retrieving bugs." \
              .format(n=self.repo_name, i=len(bug_ids))
        
        #Return copies of bugs with matching IDs
        ret_bugs = []
        for bug_id in bug_ids:
            bug = self.bugs[bug_id]
            bug = copy.deepcopy(bug) #there might be mutable attributes
            ret_bugs.append(bug)
            
        self.num_read += len(ret_bugs)
        return ret_bugs


    def update_bugs(self, bugs):
        """
        Change bugs, so that they have they same contents as the internal form.
        """
        print "Repo '{n}': received {i} bugs for updating." \
              .format(n=self.repo_name, i=len(bugs))
        self.num_updated += len(bugs)
        tnow = datetime.utcnow()
        
        for bug in bugs:
            bug_id = bug.ids[self.repo_name]
            if bug_id not in self.bugs:
                raise KeyError("Unknown bug ID: " + str(bug_id))
            bug = copy.deepcopy(bug) #there might be mutable attributes
            bug = bug._replace(ids={self.repo_name:bug_id}, time_modified=tnow)
            self.bugs[bug_id] = bug                
            
        return None
    
    
    def create_bugs(self, bugs):
        """
        Create new bugs in the remote repository.
        """
        print "Repo '{n}': received {i} bugs for creating." \
              .format(n=self.repo_name, i=len(bugs))
        self.num_created += len(bugs)
        tnow = datetime.utcnow()

        id_list = []
        for bug in bugs:
            bug = copy.deepcopy(bug) #there might be mutable attributes
            new_id = self.repo_name + "-" + str(len(self.bugs))
            bug = bug._replace(ids={self.repo_name:new_id}, 
                               time_modified=tnow, time_created=tnow) 
            self.bugs[new_id] = bug
            id_list.append(new_id)
            
        return id_list
    
    
    def delete_bugs(self, bug_ids):
        """Delete several bugs at once."""
        raise NotImplementedError("RepoControllerDummy.delete_bugs")

    
    def print_repo(self):
        """Print the repository's contents"""
        print "----------------------------------------------------------------"
        print "{name}  -  {n} bugs".format(name=self.repo_name, 
                                           n=len(self.bugs))
        print "----------------------------------------------------------------"
        print "{c} creations, {u} updates, {r} reads" \
              .format(c=self.num_created, u=self.num_updated, r=self.num_read)
        for bug in self.bugs.values():
            print bug
        print



class TracController(RepoController):
    """
    Control a Trac bug repository with XML-RPC
    
    The special value `repo_data.password="ASK"` lets the program ask 
    the user for the password.
    
    See also: 
       https://sourceforge.net/apps/trac/freeode/login/xmlrpc
       http://trac-hacks.org/wiki/XmlRpcPlugin
       
    Try it:
    server = xmlrpclib.ServerProxy("https://eike:password@sourceforge.net/apps/trac/freeode/login/xmlrpc")
    server.system.listMethods()
    
    Argument
    --------
    
    repo_data: TracData
        Description of a Trac repository.
    
    authenticate: bool
        if True, do authenticated login, do anonymous login otherwise.
        
    people_translator
        Translates people's names between the repositories.
        
    milestone_translator
        Translates names of milestones between the repositories.
        
    component_translator
        Translates names of milestones between the repositories.
    """
    def __init__(self, repo_data, authenticate = False,
                 people_translator=EquivalenceTranslatorNoop(), 
                 milestone_translator=EquivalenceTranslatorNoop()):
        RepoController.__init__(self)
        assert isinstance(repo_data, TracData)
        assert isinstance(authenticate, bool)
        assert isinstance(people_translator, EquivalenceTranslatorBase)
        assert isinstance(milestone_translator, EquivalenceTranslatorBase)
        
        self.repo_name = repo_data.repo_name
        if authenticate:
            password = repo_data.password 
            if password in (None, "ASK"):
                password = getpass("Enter password for {n}: "
                                   .format(n=repo_data.repo_name))
        else:
            password = ""
        self.server = self.create_server_proxy(repo_data.user_name, password, 
                                               repo_data.url, authenticate)
        
        #Objects to translate names between repositories and internal notation
        self.people_translator = people_translator
        self.milestone_translator = milestone_translator
        
    
    @staticmethod
    def create_server_proxy(user_name, password, server_url, authenticate):
        """
        Create a server proxy object and test it. 
        Tries password-less login if no password is given or if password does 
        not work.
        
        Format of the login URL with password:
            "https://eike:password@sourceforge.net/apps/trac/freeode/login/xmlrpc"
        Login URL without password:
            "http://sourceforge.net/apps/trac/freeode/xmlrpc"
        """
        print "Server: " + server_url
        #Break server URL into components
        url_parts = urlparse(server_url)
        #There are two API versions; old uses: "/xmlrpc", new uses "/rpc"
        if authenticate:
            print "Trying to log in with authentication to Trac..."
            login_data = [#login with password: authenticated
                          ("https", "/login/xmlrpc", 
                           "{protocol}://{user_name}:{password}@{netloc}{path}"),
                          ("https", "/login/rpc", 
                           "{protocol}://{user_name}:{password}@{netloc}{path}")]
        else:
            print "Trying to log in to Trac anonymously..."
            login_data = [#anonymous login
                          ("http", "/xmlrpc", "{protocol}://{netloc}{path}"),
                          ("http", "/rpc",    "{protocol}://{netloc}{path}")]
        
        for protocol, login_path, url_template in login_data:
            #Create URL for login 
            path = (url_parts.path + login_path).replace("//", "/") #IGNORE:E1101
            login_url = url_template \
                        .format(protocol=protocol, 
                                user_name=user_name, password=password,
                                netloc=url_parts.netloc, path=path) #IGNORE:E1101
            #print "Trying: " + login_url
            #Create XMLRPC communication object
            server = ServerProxy(login_url, allow_none=True, verbose=False)
            
            #Test the server, so that wrong password or URL are detected here
            try:
                server.system.getAPIVersion()
                print "Success! \n"
                return server
            except (ProtocolError, ResponseError, ExpatError), err: #IGNORE:W0612
                #print err, "\n"
                pass
        
        #All login attempts have failed.
        raise UserFatalError("Could not log into server: {s}"
                             .format(s=server_url))
        
        
    def get_recent_changes(self, time_since): 
        """Return list of bugs that changed since a certain date and time."""
        assert isinstance(time_since, datetime)

        bug_ids = self.server.ticket.getRecentChanges(time_since)
        bugs = self.get_bugs(bug_ids)
        return bugs
    

    def get_bugs(self, bug_ids):
        """Get specified bugs from the server. Return list of bugs"""
        assert isinstance(bug_ids, list)
        
        #Store multiple `ticket.get` requests in MultiCall object.
        multicall = MultiCall(self.server) 
        for bug_id in bug_ids: 
            multicall.ticket.get(bug_id)
        #Perform the requests in one go.
        raw_bugs = multicall()
        
        #Convert Trac objects to internal bug objects
        bugs = []
        for raw_bug in raw_bugs:
            ids = {self.repo_name: raw_bug[0]}
            creation_time = datetime(*(raw_bug[1].timetuple()[0:6]))
            modification_time = datetime(*(raw_bug[2].timetuple()[0:6]))
            short_text = safe_unicode(raw_bug[3].get("summary", None))
            long_text = safe_unicode(raw_bug[3].get("description", None))
            #Can be translated with an ``EquivalenceTranslator``
            reporter = self.people_repo2intl(raw_bug[3].get("reporter", None))
            assigned_to = self.people_repo2intl(raw_bug[3].get("owner", None))
            milestone = self.milestone_repo2intl(raw_bug[3].get("milestone", None))
            status, priority, resolution, kind = \
                self.status_trac2internal(raw_bug[3].get("status", None), 
                                          raw_bug[3].get("priority", None), 
                                          raw_bug[3].get("resolution", None), 
                                          raw_bug[3].get("type", None))
            bug = BugData(ids=ids, 
                          time_created=creation_time,       #administrative
                          time_modified=modification_time, 
                          text_short=short_text,            #text
                          text_long=long_text, 
                          reporter=reporter,                #people
                          assigned_to=assigned_to, 
                          status=status,                    #bug life cycle
                          priority=priority, 
                          resolution=resolution, 
                          kind=kind,
                          milestone=milestone               #grouping
                          )
            bugs.append(bug)
            
        return bugs
    
    
    def update_bugs(self, bugs):
        """Update contents of existing bugs."""
        #Object to store multiple XMLRPC requests.
        multicall = MultiCall(self.server) 
        
        for bug in bugs:
            #Convert internal bug to Trac form
            bug_id = bug.ids[self.repo_name]
            comment = "Automatic commit by 'bug-repo-syncer'."
            attributes = self.bug_internal2trac(bug)
            #Store `ticket.update` request in MultiCall object.
            multicall.ticket.update(bug_id, comment, attributes)
            
        #Perform the requests in one go.
        multicall()

        
    def create_bugs(self, bugs):
        """
        Create new bugs in the repository.
        
        Returns
        -------
        list[int]
            ID numbers of new bugs.
        """
        #Object to store multiple XMLRPC requests.
        multicall = MultiCall(self.server) 

        for bug in bugs:
            #Convert internal bug to Trac form
            summary = bug.text_short
            description = bug.text_long
            attributes = self.bug_internal2trac(bug)
            #Store `ticket.create` request in MultiCall object.
            multicall.ticket.create(summary, description, attributes)
            
        #Perform the requests in one go.
        id_list = multicall()
        return list(id_list)

    
    def bug_internal2trac(self, bug):
        """Convert a BugData object to a Trac ``attributes`` dict."""
        attributes = {}
        attributes["summary"] = bug.text_short
        attributes["description"] = bug.text_long
        attributes["reporter"] = self.people_intl2repo(bug.reporter)
        attributes["owner"] = self.people_intl2repo(bug.assigned_to)
        status, priority, resolution, type_ = \
            self.status_internal2trac(bug.status, bug.priority, 
                                      bug.resolution, bug.kind)
        attributes["status"] = status
        attributes["priority"] = priority
        attributes["resolution"] = resolution
        attributes["type"] = type_
        attributes["milestone"] = self.milestone_intl2repo(bug.milestone)
        return attributes
        
    
    def status_trac2internal(self, status, priority, resolution, kind):
        """
        Compute the internal status values from Trac's status values.
        
        Returns: (status, priority, resolution, kind)
        """    
        #           Trac Status  ->  internal status
        status_dict = { "new"     : "new",
                        "assigned": "confirmed",
                        "accepted": "in_progress",
                        "closed"  : "closed",     
                        "reopened": "new"}
        status = status_dict[status]
        return status, priority, resolution, kind
    
    
    def status_internal2trac(self, status, priority, resolution, kind):
        """
        Compute Trac's status values from the internal status values.
        
        Returns: (status, priority, resolution, kind)
        """    
        #           internal status ->  Trac Status
        status_dict = { "new"        : "new",
                        "confirmed"  : "assigned",
                        "in_progress": "accepted",
                        "closed"     : "closed"}
        status = status_dict[status]
        return status, priority, resolution, kind
    
    
    def delete_bugs(self, bugs_or_ids):
        """
        Delete several bugs at once. 
        
        Argument
        --------
        bugs_or_ids: list[BugData | int]
            List of bugs that should be deleted. Elements can be 
            BugData or int.
        """
        #Object to store multiple XMLRPC requests.
        multicall = MultiCall(self.server) 

        for bug in bugs_or_ids:
            if isinstance(bug, BugData):
                bug_id = bug.ids[self.repo_name]
            else:
                bug_id = bug
            #Store `ticket.delete` request in MultiCall object.
            multicall.ticket.delete(bug_id)
            
        #Perform the requests in one go.
        multicall()
      


class LaunchpadController(RepoController):
    """
    Control a Launchpad bug repository
    
    Documentation about the Launchpad API:
    
        https://help.launchpad.net/API/launchpadlib
        https://help.launchpad.net/API
        https://launchpad.net/+apidoc/1.0.html
    
    Questions about using Launchpadlib can be asked on the Launchpad 
    development mailing list (and on the developers IRC):
    
        https://launchpad.net/~launchpad-dev
    """
    def __init__(self, repo_data, authenticate=False,
                 people_translator=EquivalenceTranslatorNoop(), 
                 milestone_translator=EquivalenceTranslatorNoop()):
        """
        Arguments
        ---------
        
        repo_data: LaunchpadData
            Description of a Launchpad project.
             
        authenticate: bool
            if True, do authenticated login, do anonymous login otherwise.
            
        people_translator
            Translates people's names between the repositories.
            
        milestone_translator
            Translates names of milestones between the repositories.
            
        component_translator
            Translates names of milestones between the repositories.
        """
        RepoController.__init__(self)
        assert isinstance(repo_data, LaunchpadData)
        assert isinstance(authenticate, bool)
        assert isinstance(people_translator, EquivalenceTranslatorBase)
        assert isinstance(milestone_translator, EquivalenceTranslatorBase)
        
        self.repo_name = repo_data.repo_name
        self.launchpad = self.create_launchpad_proxy(repo_data.cachedir, 
                                                     authenticate)
        #Get project object from Launchpad
        self.project = self.launchpad.projects[repo_data.project_name]
        #Objects to translate names between repositories and internal notation
        self.people_translator = people_translator
        self.milestone_translator = milestone_translator
        
        
    @staticmethod   
    def create_launchpad_proxy(cache_dir, authenticate):
        "Log into Launchpad server and return a Launchpad (proxy) object"
        if authenticate:
            print "Trying to log in with authentication to Launchpad..."
            launchpad = Launchpad.login_with("bug-repo-syncer", "production")
        else:
            print "Trying to log in to Launchpad anonymously..."
            launchpad = Launchpad.login_anonymously(
                                    "bug-repo-syncer", "production", cache_dir)
        print "Success!"
        return launchpad
    
    
    def get_recent_changes(self, time_since): 
        """Return list of bugs that changed since a certain date and time."""
        #Get list of bug_tasks and list of associated bugs from Launchpad. 
        #The interesting information is partially in bugs and bug_tasks.
        tasks = self.project.searchTasks(
                        modified_since=time_since.strftime("%Y-%m-%dT%H:%M:%S"),
                        status=["New", "Incomplete", "Opinion", "Invalid", 
                                "Won't Fix", "Expired", "Confirmed", "Triaged", 
                                "In Progress", "Fix Committed", "Fix Released",
                                "Incomplete (with response)", 
                                "Incomplete (without response)"])
        task_list = list(tasks)
        bug_list = [lp_task.bug for lp_task in task_list]
        
        #Convert the bug_tasks to our bug format. 
        bugs = []
        for lp_task, lp_bug in zip(task_list, bug_list):
            bug = self.bug_launchpad2internal(lp_task, lp_bug)
            bugs.append(bug)
        
        return bugs


    def get_bugs(self, bug_ids):
        """
        Get specified bugs from the server. Return list of bugs
        
        Argument `bug_ids` is a list of strings. Each string is a ``self_link`` 
        URL of a ``bug_task``.
        """
        bugs = []
        for bug_id in bug_ids:
            lp_task = self.launchpad.load(bug_id) #IGNORE:E1103
            lp_bug = lp_task.bug
            bug = self.bug_launchpad2internal(lp_task, lp_bug)
            bugs.append(bug)
            
        return bugs


    def bug_launchpad2internal(self, lp_task, lp_bug):
        """
        Convert a launchpad `bug_task` and `bug` into one internal bug.
        
        On Launchpad a ``bug_task`` and a ``bug`` together contain the 
        information that we call a bug. 
        """
        ids = {self.repo_name: lp_task.self_link}
        time_created = \
            datetime.strptime(lp_bug.date_created[0:19], "%Y-%m-%dT%H:%M:%S")
        time_modified = \
            datetime.strptime(lp_bug.date_last_updated[0:19], "%Y-%m-%dT%H:%M:%S")
        text_short = lp_bug.title
        text_long = lp_bug.description
        #Can be translated with an ``EquivalenceTranslator``
        reporter = self.people_repo2intl(lp_task.owner.name)
        lp_assignee = lp_task.assignee
        assigned_to = self.people_repo2intl(lp_assignee.name) if lp_assignee else None
        lp_milestone = lp_task.milestone
        milestone = self.milestone_repo2intl(lp_milestone.name) if lp_milestone else None
        #Convert launchpad bug status to internal bug status
        status, priority, resolution, kind = \
            self.status_launchpad2internal(lp_task.status, lp_task.importance)
        
        bug = BugData(ids=ids,                        #administrative
                      time_created=time_created, 
                      time_modified=time_modified,    
                      text_short=text_short,          #text
                      text_long=text_long,               
                      reporter=reporter,              #people
                      assigned_to=assigned_to,        
                      status=status,                  #bug life cycle
                      priority=priority, 
                      resolution=resolution,  
                      kind=kind,                #grouping
                      milestone=milestone)           
        return bug
    
    
    def update_bugs(self, bugs):
        """
        Change bugs, so that they have they same contents as the internal form.
        """
        for bug in bugs:
            bug_id = bug.ids[self.repo_name]
            lp_task = self.launchpad.load(bug_id) #IGNORE:E1103
            lp_bug = lp_task.bug
            self.bug_internal2launchpad(bug, lp_task, lp_bug)
            
            
    def create_bugs(self, bugs):
        """
        Create new bugs in the remote repository.
        """
        bug_ids = []
        lp_bugs = self.launchpad.bugs #IGNORE:E1103
        for bug in bugs:
            lp_bug = lp_bugs.createBug(description="dummy", title="dummy", 
                                       target=self.project)
            lp_task = lp_bug.bug_tasks[0]
            self.bug_internal2launchpad(bug, lp_task, lp_bug)
            #The tasks's URL is used as internal bug ID
            bug_ids.append(lp_task.self_link)
            
        return bug_ids
    

    def bug_internal2launchpad(self, my_bug, lp_task, lp_bug):
        """
        Store contents of internal bug in Launchpad's task and bug entries.
        ``launchpadlib`` magically uploads the changed contents to Launchpad.
        """
        #Workaround for bug in Launchpadlib, method crashes otherwise
        #See: https://bugs.launchpad.net/launchpadlib/+bug/936502
        _ = lp_bug.title 
        
        lp_bug.title = my_bug.text_short
        lp_bug.description = my_bug.text_long
        
        lp_owner_name = self.people_intl2repo(my_bug.reporter)
        if lp_task.owner.name != lp_owner_name and lp_owner_name != "*":
            print ("Inconsistent bug reporter names: "
                   "Launchpad: {lpn}, here: {loc}"
                   .format(lpn=lp_task.owner.name, loc=lp_owner_name))
        
        lp_assignee_name = self.people_intl2repo(my_bug.assigned_to)
        if lp_assignee_name == "*":
            pass
        elif lp_assignee_name is None:
            lp_task.assignee = None
        else:
            lp_assignee=self.launchpad.people.find(text=lp_assignee_name)[0] #IGNORE:E1103
            if lp_assignee:
                lp_task.assignee = lp_assignee
            else:
                print "Unknown person in Launchpad: {p}".format(p=lp_assignee_name)
        
        lp_milestone_name = self.milestone_intl2repo(my_bug.milestone)
        if lp_milestone_name == "*":
            pass
        elif lp_milestone_name is None:
            lp_task.milestone = None
        else:
            lp_milestone = self.project.getMilestone(name=lp_milestone_name)
            if lp_milestone:
                lp_task.milestone = lp_milestone
            else:
                print ("Unknown project in Launchpad: {p}"
                       .format(p=lp_milestone_name))
        
        lp_status, lp_importance = \
            self.status_internal2launchpad(my_bug.status, my_bug.priority, 
                                           my_bug.resolution, my_bug.kind)
        if lp_status != "*":
            lp_task.status = lp_status
        if lp_importance != "*":
            lp_task.importance = lp_importance
        
        lp_task.lp_save()
        lp_bug.lp_save()
        
        
    def status_launchpad2internal(self, lp_status, lp_importance):
        """
        Compute the internal status values from Launchpad's Status and
        Importance.
        
        Returns: (status, priority, resolution, kind)
        """
        #            Launchpad Status -> status,     resolution
        status_dict = { "New":          ("new",         "none"),
                        "Incomplete":   ("new",         "none"),
                        "Opinion":      ("closed",      "invalid"),
                        "Invalid":      ("closed",      "invalid"),
                        "Won't Fix":    ("closed",      "wontfix"),
                        "Expired":      ("closed",      "none"),
                        "Confirmed":    ("confirmed",   "none"),
                        "Triaged":      ("confirmed",   "none"),
                        "In Progress":  ("in_progress", "none"),
                        "Fix Committed":("closed",      "fixed"),
                        "Fix Released": ("closed",      "fixed"),
                        "Unknown":      ("new",         "none")}
        status, resolution = status_dict[lp_status]

        #        Launchpad Importance -> priority,   kind
        importance_dict = { "Unknown":  ("major",    "defect"), 
                            "Critical": ("blocker",  "defect"),
                            "High":     ("critical", "defect"),
                            "Medium":   ("major",    "defect"),
                            "Low":      ("minor",    "defect"),
                            "Wishlist": ("*",        "enhancement"),
                            "Undecided":("major",    "defect")}
        priority, kind = importance_dict[lp_importance]
        
        return status, priority, resolution, kind
    
    
    def status_internal2launchpad(self, status, priority, resolution, kind):
        """
        Convert internal bug status to Launchpad bug status.
        
        Returns: (lp_status, lp_importance)
        """  
        #Internal status, resolution -> Launchpad Status
        if status == "new":
            lp_status = "New"
        elif status == "confirmed":
            lp_status = "Confirmed"
        elif status == "in_progress":
            lp_status = "In Progress"
        elif status == "closed":
            if resolution == "fixed":
                lp_status = "Fix Released"
            elif resolution == "invalid":
                lp_status = "Invalid"
            elif resolution == "wontfix":
                lp_status = "Won't Fix"
            else:
                lp_status = "Invalid"                
        else:
            lp_status = "*"

        #Internal priority, kind -> Launchpad Importance
        if kind == "enhancement":
            lp_importance ="Wishlist"
        elif kind == "task":
            lp_importance ="Low"
        else: #if kind in ("defect", "*"):
            if priority == "blocker":
                lp_importance ="Critical"
            elif priority == "critical":
                lp_importance ="High"
            elif priority == "major":
                lp_importance ="Medium"
            elif priority == "minor":
                lp_importance ="Low"
            elif priority == "trivial":
                lp_importance ="Low"
            else:
                lp_importance ="*"

        return lp_status, lp_importance


    def delete_bugs(self, _bugs_or_ids):
        """Delete several bugs at once."""
        raise UserFatalError("Deleting Bugs is impossible on Launchpad.")


