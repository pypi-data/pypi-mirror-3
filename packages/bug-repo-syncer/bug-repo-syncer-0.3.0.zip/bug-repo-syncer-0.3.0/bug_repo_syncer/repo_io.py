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

import copy
from xmlrpclib import ServerProxy, MultiCall, \
    ProtocolError, ResponseError, Fault
from urlparse import urlparse
from getpass import getpass
from datetime import datetime
from types import NoneType
from collections import namedtuple
from xml.parsers.expat import ExpatError
from launchpadlib.launchpad import Launchpad

from bug_repo_syncer.common import TracData, LaunchpadData, DummyRepoData, \
    BugIntl, UserFatalError, \
    EquivalenceTranslatorBase, \
    FilterBase, FilterNoop, equal_contents



def create_repo_objects(repo_data, authenticate=False, addpw={}): #IGNORE:W0102
    """
    Create objects that are directly related to the type of repository.
    These objects are necessary to create a bug pipeline.
    
    Returns
    -------
    controller: RepoController
        The repository controller, which transfers bugs over the network
        
    comparator: Callable
        A function that tests if two bugs (in repository specific format) 
        have equal contents.
        
    converter: FilterBase
        An object that converts bugs between the repository specific format,
        and the internal format.
    """
    if isinstance(repo_data, TracData):
        controller = TracController(repo_data, authenticate, addpw)
        comparator = bugtrac_equal_contents
        converter = BugTracFilter()
    elif isinstance(repo_data, LaunchpadData):
        controller = LpController(repo_data, authenticate)
        comparator = buglp_equal_contents
        converter = BugLpFilter()
    elif isinstance(repo_data, DummyRepoData):
        controller = RepoControllerDummy(repo_data)
        comparator = equal_contents
        converter = FilterNoop()
    else:
        raise UserFatalError("Unknown repository type: \n{r}."
                             .format(r=repr(repo_data)))

    return controller, comparator, converter



def safe_unicode(text):
    """
    Convert input to unicode.
    
    Argument
    --------
    text: str | unicode | None
        Text that is converted to unicode. 
        If text is already unicode it is returned unchanged.
        If text is None, None is returned.
    """
    if text is None:
        return None
    elif isinstance(text, unicode):
        return text
    elif isinstance(text, str):
        return unicode(text, encoding="utf8", errors="replace")
    else:
        raise TypeError("Argument ``text`` must be of type ``str``, "
                        "``unicode`` or ``None``. I got: " + str(type(text)))



class RepoController(object):
    """Base class of objects that control bug repositories.""" 
    def __init__(self):
        #Name of the repository. Used as key everywhere
        self.repo_name = "--undefined--"
        
    def get_recent_changes(self, time_since): 
        """Return list of bugs that changed since a certain date and time."""
        raise NotImplementedError()

    def get_bugs(self, bug_ids):
        """Get specified bugs from the server. Return list of bugs."""
        raise NotImplementedError()

    def update_bugs(self, bugs, ids):
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
    


#-------------------------- Dummy Controller ------------------------------
#==========================================================================

#``RepoControllerDummy`` does not need special classes for collaboration in a 
#bug pipeline. It works with existing components:
#
#The native bug format:
#    bug_repo_syncer.common.BugIntl
#
#The comparison function:
#    bug_repo_syncer.common.equal_contents
#
#The first filter for the bug pipeline:
#    bug_repo_syncer.common.FilterNoop

class RepoControllerDummy(RepoController):
    """
    Controller for testing.
    
    Does not connect to the Internet, but stores bugs internally
    """
    def __init__(self, repo_data, 
                 people_translator=None, 
                 milestone_translator=None, add_unknown_milestones=True):
        assert isinstance(repo_data, DummyRepoData)
        assert isinstance(people_translator, 
                          (EquivalenceTranslatorBase, NoneType))
        assert isinstance(milestone_translator, 
                          (EquivalenceTranslatorBase, NoneType))
        assert isinstance(add_unknown_milestones, bool)
        RepoController.__init__(self)
        
        #RepoController protocol
        self.repo_name = repo_data.repo_name
        self.people_translator = people_translator
        self.milestone_translator = milestone_translator
        self.add_unknown_milestones = add_unknown_milestones
        
        #Numbers of bugs read/written/created
        self.num_read = 0
        self.num_updated = 0
        self.num_created = 0
        #Internal bug storage
        self.bugs = {}
        
        #Put bugs into repository, mostly unaltered.
        if repo_data.initial_bugs:
            for bug in repo_data.initial_bugs:
                intl_id = bug.id
                #sanitize "id" and "repo_name", SyncTaskExecutor is confused by 
                #unexpected contents in this attribute.
                bug = bug._replace(repo_name=self.repo_name, id=intl_id)
                self.bugs[intl_id] = bug
            print "Initialized repository '{n}' with {i} bugs." \
                  .format(n=self.repo_name, i=len(repo_data.initial_bugs))


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


    def update_bugs(self, bugs, ids):
        """
        Change bugs, so that they have they same contents as the internal form.
        """
        print "Repo '{n}': received {i} bugs for updating." \
              .format(n=self.repo_name, i=len(bugs))
        self.num_updated += len(bugs)
        tnow = datetime.utcnow()
        
        broken_bugs = []
        
        for bug, bug_id in zip(bugs, ids):

            bug = copy.deepcopy(bug) #there might be mutable attributes
            bug = bug._replace(repo_name=self.repo_name, id=bug_id, 
                               time_modified=tnow)
            if bug_id in self.bugs:
                self.bugs[bug_id] = bug
            else:
                print ("Warning: could not update bug. Unknown bug ID: " 
                       + str(bug_id))
                broken_bugs.append(bug)
        
        return broken_bugs
    
    
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
            new_id = self.repo_name[-1] + str(len(self.bugs))
            bug = bug._replace(repo_name=self.repo_name, id=new_id,
                               time_modified=tnow, 
                               time_created=tnow) 
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



#--------------------------- Trac Controller ------------------------------
#==========================================================================
"""
Bug data for the Trac repository.

  ----------------------------------------
            Bug Status Values               
  ----------------------------------------
  Status   Priority Resolution Type       
  -------- -------- ---------- -----------
  new      blocker  fixed      defect     
  assigned critical invalid    enhancement
  accepted major    wontfix    task       
  closed   minor    duplicate             
  reopened trivial  worksforme            
                    None                  
  ----------------------------------------
""" #IGNORE:W0105
BugTrac = namedtuple("BugTrac", 
                     "repo_name, id,"                        #administrative
                     "time_created, time_modified,"
                     "summary, description,"                 #text
                     "reporter, owner,"                      #people
                     "status, priority, resolution, type,"   #bug life cycle
                     "milestone,")                           #grouping
    
    
BUGTRAC_CONTENTS_FIELDS = list(set(BugTrac._fields).difference( #IGNORE:E1101
                        ["repo_name", "id", "time_created", "time_modified"]))
def bugtrac_equal_contents(bug1, bug2):
    """ 
    Test if bugs are equal, but ignore fields that the repositories 
    always change. 
    """
    for fname in BUGTRAC_CONTENTS_FIELDS:
        if getattr(bug1, fname) != getattr(bug2, fname):
            return False
    return True


class BugTracFilter(FilterBase):
    """Convert a bug between Trac's format and internal format."""
    
    def intl2repo(self, bug):
        """Translate: internal -> Trac."""
        assert isinstance(bug, BugIntl)
        status, priority, resolution, type_ = self.status_internal2trac(
                            bug.status, bug.priority, bug.resolution, bug.kind)
        bug_tr = BugTrac(repo_name=bug.repo_name, 
                         id=bug.id,
                         time_created=bug.time_created, 
                         time_modified=bug.time_modified,
                         summary=bug.text_short,
                         description=bug.text_long,
                         reporter=bug.reporter,
                         owner=bug.assigned_to,
                         status=status, priority=priority, 
                         resolution=resolution, type=type_,
                         milestone=bug.milestone)
        return bug_tr
    
    
    def repo2intl(self, bug):
        """Translate: Trac -> internal."""
        assert isinstance(bug, BugTrac)
        status, priority, resolution, kind = self.status_trac2internal(
                            bug.status, bug.priority, bug.resolution, bug.type)
        bug_i = BugIntl(repo_name=bug.repo_name, 
                        id=bug.id,
                        time_created=bug.time_created, 
                        time_modified=bug.time_modified,
                        text_short=bug.summary,
                        text_long=bug.description,
                        reporter=bug.reporter,
                        assigned_to=bug.owner,
                        status=status, priority=priority, 
                        resolution=resolution, kind=kind,
                        milestone=bug.milestone)
        return bug_i


    def status_internal2trac(self, status, priority, resolution, kind):
        """
        Compute Trac's status values from the internal status values.
        (Changes only `status`.)
        
        Returns: (status, priority, resolution, kind)
        """    
        #           internal status ->  Trac Status
        status_dict = { "new"        : "new",
                        "confirmed"  : "assigned",
                        "in_progress": "accepted",
                        "closed"     : "closed"}
        status = status_dict[status]
        type_ = kind
        return status, priority, resolution, type_
    
    
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
    
    

class TracController(RepoController):
    """
    Control a Trac bug repository with XML-RPC
    
    The special value `repo_data.password=None` lets the program ask 
    the user for the password.
    
    See also: 
       https://sourceforge.net/apps/trac/freeode/login/xmlrpc
       http://trac-hacks.org/wiki/XmlRpcPlugin
       
    Try it:
    server = xmlrpclib.ServerProxy("https://eike:password@sourceforge.net/apps/trac/freeode/login/xmlrpc")
    server.system.listMethods()
    """
    def __init__(self, repo_data, authenticate=False, addpw={}): #IGNORE:W0102
        """
        Argument
        --------
        
        repo_data: TracData
            Description of a Trac repository.
        
        authenticate: bool
            if True, do authenticated login, do anonymous login otherwise.
            
        addpw: dict[str,str]
            Dictionary of additional passwords, useful for testing.
            repository name -> password.
        """
        RepoController.__init__(self)
        assert isinstance(repo_data, TracData)
        assert isinstance(authenticate, bool)
        assert isinstance(addpw, dict)
        
        self.repo_name = repo_data.repo_name
        if authenticate:
            password = repo_data.password 
            passworda = addpw.get(self.repo_name, None)
            if passworda:
                password = passworda
            elif password is None:
                password = getpass("Enter password for {n}: "
                                   .format(n=repo_data.repo_name))
        else:
            password = ""
        self.server = self.create_server_proxy(repo_data.user_name, password, 
                                               repo_data.url, authenticate)
            
    
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
            print "Trying to log in to Trac with authentication..."
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
                ver = server.system.getAPIVersion() #IGNORE:W0612
                #ver_str = "(API version: {})".format(".".join(map(str, ver)))
                print "Success!"
                return server
            except (ProtocolError, ResponseError, ExpatError), err: #IGNORE:W0612
                #print err, "\n"
                pass
        
        #All login attempts have failed.
        raise UserFatalError("Could not log into server: {s}"
                             .format(s=server_url))
        
        
    def get_recent_changes(self, time_since): 
        """Return list of bugs that changed since a certain date and time."""
        #TODO: maybe return: bugs, bug_ids
        #      this would be nicer for use in small scripts.
        assert isinstance(time_since, datetime)

        bug_ids = self.server.ticket.getRecentChanges(time_since)
        bugs = self.get_bugs(bug_ids)
        return bugs
    

    def get_bugs(self, ids):
        """Get specified bugs from the server. Return list of bugs"""
        assert isinstance(ids, list)
        
        #Store multiple `ticket.get` requests in MultiCall object.
        multicall = MultiCall(self.server) 
        for bug_id in ids: 
            multicall.ticket.get(bug_id)
        #Perform the requests in one go.
        raw_bugs = multicall()

        #Convert Trac objects to internal bug objects
        bugs = []
        for raw_bug in raw_bugs:
            attrs = raw_bug[3]
            bug = BugTrac(
                #administrative
                repo_name    =self.repo_name,
                id           =str(raw_bug[0]), 
                time_created =datetime(*(raw_bug[1].timetuple()[0:6])),
                time_modified=datetime(*(raw_bug[2].timetuple()[0:6])),
                #text
                summary    =safe_unicode(attrs.get("summary", None)),
                description=safe_unicode(attrs.get("description", None)),
                #people
                reporter=safe_unicode(attrs.get("reporter", None)),
                owner   =safe_unicode(attrs.get("owner", None)),
                #bug life cycle
                status    =attrs.get("status", None),
                priority  =attrs.get("priority", None),
                resolution=attrs.get("resolution", None),
                type      =attrs.get("type", None),
                #grouping
                milestone=safe_unicode(attrs.get("milestone", None)))
            bugs.append(bug)
            
        return bugs
    
    
    def update_bugs(self, bugs, ids):
        """Update contents of existing bugs."""
        #Object to store multiple XMLRPC requests.
        multicall = MultiCall(self.server) 
        
        for bug, bug_id in zip(bugs, ids):
            assert isinstance(bug, BugTrac)
            #Convert internal bug to Trac form
            comment = "Automatic commit by 'bug-repo-syncer'."
            attrs = self.conv_bug2attrs(bug)
            #Store `ticket.update` request in MultiCall object.
            multicall.ticket.update(bug_id, comment, attrs)
            
        #Perform the requests in one go.
        resit = multicall()
        
        #Get bugs that could not be uploaded
        broken_bugs = []
        for i in range(len(bugs)):
            try:
                resit[i] #raise xmlrpclib.Fault for bug where error happened
            except Fault, err:
                print ("Warning: could not upload bug {bug_id}. Error: {err}"
                       .format(bug_id=ids[i], err=repr(err)))
                broken_bugs.append(bugs[i]._replace(
                                        id=ids[i], repo_name=self.repo_name))           
        return broken_bugs

        
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
            assert isinstance(bug, BugTrac)
            #Convert internal bug to Trac form
            summary = bug.summary
            description = bug.description
            attributes = self.conv_bug2attrs(bug)
            #Store `ticket.create` request in MultiCall object.
            multicall.ticket.create(summary, description, attributes)
            
        #Perform the requests in one go.
        ids = multicall()
        str_ids = [str(bug_id) for bug_id in ids]
        return str_ids


    def conv_bug2attrs(self, bug):
        """Convert a BugTrac object to a Trac ``attrs`` dict."""
        attrs = {}
        attrs["summary"] = bug.summary
        attrs["description"] = bug.description
        attrs["reporter"] = bug.reporter
        attrs["owner"] = bug.owner
        attrs["status"] = bug.status
        attrs["priority"] = bug.priority
        attrs["resolution"] = bug.resolution
        attrs["type"] = bug.type
        attrs["milestone"] = bug.milestone
        return attrs
        
    
    def delete_bugs(self, ids):
        """
        Delete several bugs at once. 
        
        Argument
        --------
        ids: list[int]
            List of bugs that should be deleted. 
        """
        #Object to store multiple XMLRPC requests.
        multicall = MultiCall(self.server) 

        for bug_id in ids:
            #Store `ticket.delete` request in MultiCall object.
            multicall.ticket.delete(bug_id)
            
        #Perform the requests in one go.
        multicall()
      


#----------------------- Launchpad Controller -----------------------------
#==========================================================================
"""
Bug data for the Launchpad repository.

  ------------------------
     Bug Status Values               
  ------------------------
  Status        Importance
  ------------- ----------
  New           Unknown   
  Incomplete    Critical  
  Opinion       High      
  Invalid       Medium    
  Won't Fix     Low       
  Expired       Wishlist  
  Confirmed     Undecided 
  Triaged                 
  In Progress             
  Fix Committed           
  Fix Released            
  Unknown                 
  ------------------------
""" #IGNORE:W0105
BugLp = namedtuple("BugLp", 
                   "repo_name, id,"                   #administrative
                   "time_created, time_modified,"
                   "title, description,"              #text
                   "owner, assignee,"                 #people
                   "status, importance,"              #bug life cycle
                   "milestone,")                      #grouping


BUGLP_CONTENTS_FIELDS = list(set(BugLp._fields).difference( #IGNORE:E1101
                        ["repo_name", "id", "time_created", "time_modified"]))
def buglp_equal_contents(bug1, bug2):
    """ 
    Test if bugs are equal, but ignore fields that the repositories 
    always change. 
    """
    for fname in BUGLP_CONTENTS_FIELDS:
        if getattr(bug1, fname) != getattr(bug2, fname):
            return False
    return True


class BugLpFilter(FilterBase):
    """Convert a bug between Launchpad's format and internal format."""
    
    def intl2repo(self, bug):
        """Translate: internal -> repository."""
        lp_status, lp_importance = self.status_internal2launchpad(
                            bug.status, bug.priority, bug.resolution, bug.kind)
        bug_lp = BugLp(repo_name    =bug.repo_name,     #administrative
                       id           =bug.id,
                       time_created =bug.time_created,
                       time_modified=bug.time_modified,
                       title        =bug.text_short,    #text
                       description  =bug.text_long,               
                       owner        =bug.reporter,      #people
                       assignee     =bug.assigned_to,        
                       status       =lp_status,         #bug life cycle
                       importance   =lp_importance,                
                       milestone    =bug.milestone)     #grouping
        return bug_lp 
    
    
    
    def repo2intl(self, bug):
        """Translate: repository -> internal."""
        status, priority, resolution, kind = \
                self.status_launchpad2internal(bug.status, bug.importance)
        bug_i = BugIntl(repo_name   =bug.repo_name,         #administrative
                        id          =bug.id,
                        time_created=bug.time_created, 
                        time_modified=bug.time_modified,
                        text_short  =bug.title,             #text
                        text_long   =bug.description,
                        reporter    =bug.owner,             #people
                        assigned_to =bug.assignee,
                        status      =status,                #bug life cycle
                        priority    =priority, 
                        resolution  =resolution, 
                        kind        =kind,
                        milestone   =bug.milestone)         #grouping
        return bug_i



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


    
class LpController(RepoController):
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
    def __init__(self, repo_data, authenticate=False):
        """
        Arguments
        ---------
        
        repo_data: LaunchpadData
            Description of a Launchpad project.
             
        authenticate: bool
            if True, do authenticated login, do anonymous login otherwise.
        """
        RepoController.__init__(self)
        assert isinstance(repo_data, LaunchpadData)
        assert isinstance(authenticate, bool)
        
        self.repo_name = repo_data.repo_name
        self.launchpad, self.project = self.create_launchpad_proxy(
                                                        repo_data, authenticate)
        
        
    @staticmethod   
    def create_launchpad_proxy(repo_data, authenticate):
        "Log into Launchpad server and return Launchpad, and project objects."
        print "Server: " + repo_data.server
        try:
            if authenticate:
                print "Trying to log in to Launchpad with authentication..."
                launchpad = Launchpad.login_with(
                                            "bug-repo-syncer", repo_data.server)
            else:
                print "Trying to log in to Launchpad anonymously..."
                launchpad = Launchpad.login_anonymously(
                        "bug-repo-syncer", repo_data.server, repo_data.cachedir)
            #Get project object from Launchpad
            project = launchpad.projects[repo_data.project_name] #IGNORE:E1103
        except (KeyError, ValueError) as err:
            raise UserFatalError(
                "Could not log into Launchpad and access project '{p}'.\n\t{e}"
                .format(p=repo_data.project_name, e=str(err)))
        
        print "Success!"
        return launchpad, project
    
    
    def get_recent_changes(self, time_since): 
        """Return list of bugs that changed since a certain date and time."""
        #TODO: maybe return: bugs, bug_ids
        #      this would be nicer for use in small scripts.
        #Get list of bug_tasks and list of associated bugs from Launchpad. 
        #The interesting information is partially in bugs and bug_tasks.
        tasks = self.project.searchTasks(
                        modified_since=time_since.strftime("%Y-%m-%dT%H:%M:%S"),
                        status=["New", "Incomplete", "Opinion", "Invalid", 
                                "Won't Fix", "Expired", "Confirmed", "Triaged", 
                                "In Progress", "Fix Committed", "Fix Released"])
        task_list = list(tasks)
        bug_list = [lp_task.bug for lp_task in task_list]
        
        #Convert the bug_tasks to our bug format. 
        bugs = []
        for lp_task, lp_bug in zip(task_list, bug_list):
            bug = self.conv_launchpad2bug(lp_task, lp_bug)
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
            lp_bug = self.launchpad.bugs[bug_id] #IGNORE:E1103
            lp_task = self.find_bug_task(lp_bug)
            bug = self.conv_launchpad2bug(lp_task, lp_bug) 
            bugs.append(bug)
            
        return bugs


    def find_bug_task(self, lp_bug):
        """
        Search for a bug-task in a bug, that is in (targeted to) our project.
        """
        #Search for bug-task that belongs to our project
        for lp_task in lp_bug.bug_tasks:
            if lp_task.target == self.project:
                return lp_task
        else:
            raise KeyError("Bug {id} not in '{proj}'."
                           .format(id=lp_bug.id, proj=self.project.name))
        

    def conv_launchpad2bug(self, lp_task, lp_bug):
        """
        Convert a launchpad `bug_task` and `bug` into one BugLp instance.
        
        On Launchpad a ``bug_task`` and a ``bug`` together contain the 
        information that we call a bug. 
        """
        repo_name = self.repo_name
        bug_id = str(lp_bug.id)
        time_created = datetime.strptime(
                            lp_bug.date_created[0:19], "%Y-%m-%dT%H:%M:%S")
        time_modified = datetime.strptime(
                            lp_bug.date_last_updated[0:19], "%Y-%m-%dT%H:%M:%S")
        title = lp_bug.title
        description = lp_bug.description
        owner = lp_task.owner.name
        lp_assignee = lp_task.assignee
        assignee = lp_assignee.name if lp_assignee else None
        status = lp_task.status
        importance = lp_task.importance
        lp_milestone = lp_task.milestone
        milestone = lp_milestone.name if lp_milestone else None
        
        bug = BugLp(repo_name=repo_name,            #administrative
                    id=bug_id,
                    time_created=time_created,
                    time_modified=time_modified,
                    title=title,                  #text
                    description=description,               
                    owner=owner,            #people
                    assignee=assignee,        
                    status=status,                #bug life cycle
                    importance=importance,                
                    milestone=milestone)          #grouping
        return bug
    
    
    def update_bugs(self, bugs, ids):
        """
        Change bugs, upload the bugs' contents to the repository.
        
        Arguments
        ---------
        bugs: list[BugLp]
            The bugs that will be uploaded.
        ids: list[str | int]
            IDs of the bugs that will be uploaded.
            
        Returns
        -------
        broken_bugs: list[BugLp]
            Bugs that could not be uploaded.
        """
        broken_bugs = []
        for bug, bug_id in zip(bugs, ids):
            assert isinstance(bug, BugLp)
            try:
                lp_bug = self.launchpad.bugs[bug_id] #IGNORE:E1103
                lp_task = self.find_bug_task(lp_bug)
                self.conv_bug2launchpad(bug, lp_task, lp_bug)
            except KeyError as err:
                print ("Warning: could not upload bug {bug_id}. Error: {err}"
                       .format(bug_id=bug_id, err=repr(err)))
                broken_bugs.append(bug._replace(
                                        id=bug_id, repo_name=self.repo_name))    
        return broken_bugs
    
            
    def create_bugs(self, bugs):
        """
        Create new bugs in the remote repository.
        """
        bug_ids = []
        lp_bugs = self.launchpad.bugs #IGNORE:E1103
        for bug in bugs:
            assert isinstance(bug, BugLp)
            lp_bug = lp_bugs.createBug(description="dummy", title="dummy", 
                                       target=self.project)
            lp_task = lp_bug.bug_tasks[0]
            self.conv_bug2launchpad(bug, lp_task, lp_bug)
            bug_ids.append(str(lp_bug.id))
            
        return bug_ids
    

    def conv_bug2launchpad(self, my_bug, lp_task, lp_bug):
        """
        Store contents of internal bug in Launchpad's task and bug entries.
        ``launchpadlib`` magically uploads the changed contents to Launchpad.
        """
        #Workaround for bug in Launchpadlib, method crashes otherwise
        #See: https://bugs.launchpad.net/launchpadlib/+bug/936502
        #TODO: remove?
#        _ = lp_bug.title 
        lp_bug.title = my_bug.title
        lp_bug.description = my_bug.description
        
        lp_owner_name = my_bug.owner
        if lp_task.owner.name != lp_owner_name and lp_owner_name != "*":
            print ("Inconsistent bug reporter names: "
                   "Launchpad: {lpn}, here: {loc}"
                   .format(lpn=lp_task.owner.name, loc=lp_owner_name))
        
        lp_assignee_name = my_bug.assignee
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
        
        lp_milestone_name = my_bug.milestone
        if lp_milestone_name == "*":
            pass
        elif lp_milestone_name is None:
            lp_task.milestone = None
        else:
            lp_milestone = self.project.getMilestone(name=lp_milestone_name)
            if lp_milestone:
                lp_task.milestone = lp_milestone
            else:
                print ("Unknown milestone in Launchpad: {p}"
                       .format(p=lp_milestone_name))
        
        if my_bug.status != "*":
            lp_task.status = my_bug.status
        if my_bug.importance != "*":
            lp_task.importance = my_bug.importance
        
        lp_task.lp_save()
        lp_bug.lp_save()
        
        
    def delete_bugs(self, _ids):
        """Delete several bugs at once."""
        raise UserFatalError("Deleting Bugs is impossible on Launchpad.")

