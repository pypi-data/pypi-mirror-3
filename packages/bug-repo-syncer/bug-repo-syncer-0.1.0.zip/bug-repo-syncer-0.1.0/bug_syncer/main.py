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
Top level functionality
"""
#Warning: access to private attributes (``foo._xxx``).
#pylint: disable=W0212 

from __future__ import division
from __future__ import absolute_import              

import sys
import os  
import copy
import shutil
import argparse
import difflib 
from cPickle import Pickler, Unpickler 
from datetime import datetime
from dateutil import parser as date_parser
from tempfile import mkstemp
from subprocess import Popen, PIPE
from itertools import chain

import bug_syncer.example_conf
from bug_syncer.repo_io import TracController, LaunchpadController, \
    RepoControllerDummy
from bug_syncer.common import TracData, LaunchpadData, DummyRepoData, BugData, \
    SyncTaskData, BugMergeTask, BugWriteTask, \
    UserFatalError, UnknownWordError, EquivalenceTranslator


class ApplicationMain(object):
    """
    Main object of bug synchronization program 
    """
    def __init__(self):
        #name of configuration file
        self.conf_name = "syncer_config.py"
        #name of datafile
        self.data_name = "sync-data.pickle"
        
        #Directory for the configuration file and for the data that the 
        #application saves. 
        self.project_dir = ""
        #The configuration of the repositories
        self.repo_config = SyncTaskData(None, None, None, None)
        
        #Per run information - written at end of run
        #Date and time of last synchronization 
        self.last_sync = datetime(1970, 1, 1)
        #List of known synchronized bugs
        self.known_bugs = []


    def main(self):
        """
        The program's main routine. This function should be called by a trivial 
        start script.
        """
        #Catch UserFatalError and show error message to the user.
        try:
            #Parse command line
            cmdinfo = self.parse_args(sys.argv[1:])
            
            #The user can specify a project directory, defaults to cwd
            self.project_dir = cmdinfo.project_dir[0] if cmdinfo.project_dir else \
                               os.getcwd() 
            
            #Do the work
            if cmdinfo.command == "init":
                self.do_init()
            elif cmdinfo.command == "info":
                self.do_info()
            elif cmdinfo.command == "sync":
                self.do_sync(cmdinfo)
            else:
                raise Exception("Unimplemented command: " + cmdinfo.command)
            
        except UserFatalError, err:
            print "Error: ", err
            print


    def parse_args(self, args=None):
        """
        Parse the command line arguments
        
        Argument
        --------
        args: list[str] | None
            The arguments that are parsed. 
        """
        #Create the parser, define error and help messages ---
        parser = argparse.ArgumentParser(description='Synchronize bug repositories.')
        
        #Define general options
        parser.add_argument(
            "--project-dir", dest="project_dir", action="store", nargs=1, 
            default=None, required=False, metavar="DIRECTORY",
            help="specify directory with configuration and data files")
        
        #Define commands 
        subparsers = parser.add_subparsers(
            dest='command', title="Commands", help="",
            description="To get help on a command use: %(prog)s COMMAND --help")
        parser_init = subparsers.add_parser( #IGNORE:W0612
            "init", help="create configuration files in the current directory")
        parser_stat = subparsers.add_parser( #IGNORE:W0612
            "info", help="show status of project directory")
        parser_sync = subparsers.add_parser(
            "sync", help="synchronize the repositories")
        #TODO: validate and convert option with ``type=...`` argument; see:
        #        http://docs.python.org/library/argparse.html#type
        parser_sync.add_argument(
            "--since", dest="time_since", action="store", nargs=1, 
            default=None, required=False, metavar="DATE_TIME",
            help="consider changes since this date (and time)")
        
        #Parse the arguments ---
        return parser.parse_args(args)


    def do_init(self):
        """
        Perform the 'init' command. 
        Initialize a project directory.
        """
        #Check for writable directory
        ok_dir, msg = self.check_file(self.project_dir, 
                                      isdir=True, read=True, write=True)
        if not ok_dir:
            print "Project directory: \n" + self.project_dir
            print "Problem: {m} \n".format(m=msg)
            raise UserFatalError("Can not write configuration files.")
        
        #Check for existing configuration
        confpath = os.path.join(self.project_dir, self.conf_name)
        ok_conf, _ = self.check_file(confpath, 
                                     isdir=False, read=True, write=False)
        if ok_conf:
            print "There is an existing configuration file, renaming it."
            shutil.move(confpath, confpath + "." + str(datetime.utcnow()))
        
        #Copy the example_conf module into the project directory
        #remove ".pyc" extension and put ".py" there
        examplepath = bug_syncer.example_conf.__file__.rsplit(".",1)[0] + ".py" 
        with open(examplepath, "r") as origfile:
            lines = origfile.readlines()
        #Cut the copyright header off
        n=0
        for n, line in enumerate(lines):
            if line.startswith("#@@@[[[-----------"):
                break
        with open(confpath, "w") as outfile:
            outfile.writelines(lines[n+1:])
        
        print "Wrote example configuration file:"
        print confpath
        print "You have to edit it to suit your repositories."
        print
        
        
    def do_info(self):
        """
        Perform the 'info' command. 
        Display information about the project.
        """
        #Test access to project directory and files that we expect there
        #Directory must we readable and writable
        print "Project directory:  '{d}'".format(d=self.project_dir)
        ok_dir, msg = self.check_file(self.project_dir, 
                                      isdir=True, read=True, write=True)
        if not ok_dir:
            print "Problem: {m} \n".format(m=msg)
            
        #The configuration file must be readable
        confpath = os.path.join(self.project_dir, self.conf_name)
        print "Configuration file: '{f}'".format(f=confpath)
        ok_conf, msg = self.check_file(confpath, 
                                       isdir=False, read=True, write=False)
        if not ok_conf:
            print "Problem: {m} \n".format(m=msg)
        
        #The data file might exist 
        datapath = os.path.join(self.project_dir, self.data_name)
        print "Data file:          '{f}'".format(f=datapath)
        exist_data, msg = self.check_file(datapath, 
                                          isdir=False, read=False, write=False)
        if not exist_data:
            print "No stored data."
            
        #Without configuration file it makes no sense to go further
        if not ok_conf:
            print
            raise UserFatalError("No working configuration!")
        print
        
        #Test configuration and stored data
        self.read_data()
        print "Repositories: ",
        for repo in self.repo_config.repos_list:
            print repo.repo_name + ", ",
        #TODO: implement: get repository URL - also for Launchpad.
        print 
        print "Known bugs: " + str(len(self.known_bugs))
        print
        
    
    def do_sync(self, cmdinfo):
        """
        Perform the 'sync' command. 
        Synchronize the bug repositories
        """
        errmsg = ""
        #Project directory must we readable and writable
        ok_dir, msg = self.check_file(self.project_dir, 
                                      isdir=True, read=True, write=True)
        errmsg += "Project directory: {m}. ".format(m=msg) if not ok_dir else ""
        #The configuration file must be readable
        confpath = os.path.join(self.project_dir, self.conf_name)
        ok_conf, msg = self.check_file(confpath, 
                                       isdir=False, read=True, write=False)
        errmsg += "Configuration file: {m}. ".format(m=msg) if not ok_conf else ""
        if not (ok_dir and ok_conf):
            raise UserFatalError("Broken configuration! \n" + errmsg)
        
        #Read configuration and stored bugs from disk    
        self.read_data()        
        #Interpret option "--since"
        sync_since = self.last_sync
        if cmdinfo.time_since:
            sync_since = date_parser.parse(cmdinfo.time_since[0], 
                                           yearfirst=True)
        #Do the synchronization
        syncer = SyncTaskExecutor(self.repo_config, self.known_bugs, 
                                  authenticate=True)
        self.last_sync, self.known_bugs = syncer.synchronize_repos(sync_since)
        #write known bugs and sync time to disk
        self.write_data()
        
        
    @staticmethod
    def check_file(path, isdir=False, read=False, write=False):
        """Check facts about a file/directory."""
        if not os.path.exists(path):
            return False, "does not exist"
        if isdir and not os.path.isdir(path):
            return False, "is no directory"
        if not isdir and not os.path.isfile(path):
            return False, "is no regular file"        
        msgs = []
        ok = True
        if read and not os.access(path, os.R_OK):
            msgs += ["no read permission"]
            ok = False
        if write and not os.access(path, os.W_OK):
            msgs += ["no write permission"]
            ok = False
            
        msg = ", ".join(msgs)
        return ok, msg
    
        
    def read_data(self):
        """Read configuration and run-to-run data."""
        #Import configuration file - yes, hack
        oldpath = sys.path
        try:
            sys.path = [self.project_dir] + sys.path
            conf_module = self.conf_name[:-3] #remove ".py"
            config = __import__(conf_module, globals(), locals(), [], 0)
            sys.path = oldpath
            #Get the configuration
            self.repo_config = config.repo_config 
            assert isinstance(config.repo_config, SyncTaskData), \
                   "repo_config must be a ``SyncTaskData`` object."
        except Exception, err:
            raise UserFatalError("Broken configuration file!\n" + str(err))
        finally:
            sys.path = oldpath #do this in any case
            
        #Load stored run-to-run data
        dataname = os.path.join(self.project_dir, self.data_name)
        if os.access(dataname, os.R_OK):
            with open(dataname, "rb") as datafile:
                unp = Unpickler(datafile)
                self.last_sync = unp.load()
                self.known_bugs = unp.load()


    def write_data(self):
        """Store run-to-run data on disk"""
        #Save data to disk
        dataname = os.path.join(self.project_dir, self.data_name)
        tempname = dataname + ".tmp"
        with open(tempname, "wb") as tempfile:
            pic = Pickler(tempfile, protocol=-1)
            pic.dump(self.last_sync)
            pic.dump(self.known_bugs)
        shutil.move(tempname, dataname)



def split(condition, iterable):
    """
    Split a container according to a condition.
    
    Arguments
    ---------
    condition: callable
        A function with one argument, that is called for every element in 
        `iterable`. It must return True when the condition is met, and False
        otherwise.
    iterable: 
        The container that is split. 
        
    Returns
    -------
    true_list: list
        Elements of iterable where the condition is true.
    false_list: list
        Elements of iterable where the condition is false.
    """
    true_list, false_list = [], []
    for elm in iterable:
        if condition(elm):
            true_list.append(elm)
        else:
            false_list.append(elm)
            
    return true_list, false_list



#BUG_CONTENTS_FIELDS = list(set(BugData._fields).difference(
#                                    ["ids", "time_created", "time_modified"]))
#def equal_contents(bug1, bug2):
#    """ 
#    Test if bugs are equal, but ignore fields that the repositories 
#    always change. (ids, time_created, time_modified)
#    """
#    for fname in BUG_CONTENTS_FIELDS:
#        if getattr(bug1, fname) != getattr(bug2, fname):
#            return False
#    return True

def make_bugs_comparable(bug):
    """
    Set bugs to neutral state, so that it can be compared.
    TODO: copying two bugs for every comparison is a waste of resources
    """
    return bug._replace(ids={}, time_created=None, time_modified=None)



class SyncTaskExecutor(object):
    """
    Synchronize two or more repositories.
    
    Steps:
    * Download bugs from repositories, and translate them to the internal 
      format. -> BugData
    * Identify bugs that belong together. They are different versions of 
      the same bug, and must be synchronized. -> BugMergeTask
    * Merge bugs 
    * Upload merged bugs to repository, and transform them to repository 
      specific format. 
    """
    def __init__(self, task_data, synched_bugs=[],              #IGNORE:W0102
                 authenticate=False): 
        
        assert isinstance(task_data, SyncTaskData)
        assert isinstance(synched_bugs, (list, tuple))
        assert isinstance(authenticate, bool)
        
        #Objects for: read/write bugs over network, convert bug format
        self.repo_controllers = self.create_repo_controllers(
                task_data.repos_list, authenticate, 
                task_data.people_translator, task_data.milestone_translator)
        #List of known synchronized bugs
        self.known_bugs = list(synched_bugs)
        #Internal ID is index into ``self.known_bugs``
        self.id_translator = self.create_id_translator(task_data.repos_list, 
                                                       synched_bugs)
        
        
    def _get_repo_names(self):
        """Return list of repositories that are synchronized by this object."""
        return [ctrl.repo_name for ctrl in self.repo_controllers]
    repo_names = property(_get_repo_names)
    
    
    @staticmethod
    def create_repo_controllers(repo_data_list, authenticate, 
                                people_translator, milestone_translator):
        """
        Create the repository controllers. These objects read/write bugs over 
        the network, convert bugs to/from local format.
        """
        repo_names = set()
        controllers = []
        for rdata in repo_data_list:
            if isinstance(rdata, TracData):
                controllers.append(TracController(rdata,  authenticate,
                                                  people_translator, 
                                                  milestone_translator))
            elif isinstance(rdata, LaunchpadData):
                controllers.append(LaunchpadController(rdata, authenticate, 
                                                       people_translator, 
                                                       milestone_translator))
            elif isinstance(rdata, DummyRepoData):
                controllers.append(RepoControllerDummy(rdata))
            else:
                raise UserFatalError("Unknown repository type: \n{r}."
                                     .format(r=repr(rdata)))
            
            #Test: repo_names must be unique
            if rdata.repo_name in repo_names:
                raise UserFatalError("Duplicate repository name: '{n}'." \
                                .format(n=rdata.repo_name))
            repo_names.add(rdata.repo_name)
        
        return controllers


    @staticmethod
    def create_id_translator(repo_data_list, synched_bugs):
        """Create equivalence translator for bug IDs"""
        #Create empty translator
        repos = [repo.repo_name for repo in repo_data_list] + ["INTERNAL"]
        tranlator = EquivalenceTranslator(repos, [])
        
        #fill translator with data from synched_bugs
        for intl_id, bug in enumerate(synched_bugs):
            line = [bug.ids[repo] for repo in repos[:-1]] + [intl_id]
            tranlator.add_table_line(line)
            #update the bug's internal ID 
            bug.ids["INTERNAL"] = intl_id
            
        return tranlator
    
    
    def test_bug_consistency(self, bug):
        """Test if bug is without errors."""
        assert isinstance(bug, BugData)
        #The bug must contain its IDs in all repositories. Its internal ID
        #might be added in ``known_bug_add``
        si = set(["INTERNAL"])
        assert set(bug.ids.keys()).difference(si) == \
               set(self.id_translator.repo_names).difference(si)
        
        
    def known_bug_add(self, bug):
        """
        Add a new bug to the storage for synchronized bugs.
        
        ``bug.ids`` must contain the ID:repo associations for all repositories.
        Otherwise this function raises a ``KeyError``.
        """
        self.test_bug_consistency(bug)
        
        #Copy bug, so no one can modify its mutable attributes
        bug = copy.deepcopy(bug)
        
        #Append bug to storage
        intl_id = len(self.known_bugs)
        self.known_bugs.append(bug)
        #update the bug's internal ID 
        bug.ids["INTERNAL"] = intl_id
        
        #Create new entry in object to translate bug IDs between repositories
        repos = self.id_translator.repo_names
        line = [bug.ids[repo] for repo in repos[:-1]] + [intl_id]
        self.id_translator.add_table_line(line)
        
        return intl_id
        
        
    def known_bug_update(self, bug):
        """
        Exchange a bug with an updated version of it, in the storage for 
        synchronized bugs.
        """
        self.test_bug_consistency(bug)
        
        #Get internal ID from bug.
        try:
            intl_bug_id = bug.ids["INTERNAL"]
        except UnknownWordError:
            raise KeyError("Unknown bug: \n" + repr(bug))
        
        #Copy bug, so no one can modify its mutable attributes
        bug = copy.deepcopy(bug)        
        self.known_bugs[intl_bug_id] = bug
        
    
    def known_bug_find(self, repo_name, bug_id):
        """
        Find a known bug, by its ID from any of the repositories.
        
        Returns
        -------
        bug, internal_bug_id
        """
        try:
            intl_id = self.id_translator.repo2intl(repo_name, bug_id)
        except UnknownWordError:
            return None, None
        
        bug = self.known_bugs[intl_id] 
        return bug, intl_id
        
        
    def get_recent_changes(self, time_since): 
        """
        Return bugs that changed since a certain date and time.
        
        Arguments
        ---------
        time_since: datetime
        
        Returns
        -------
        list[list[BugData]]
            The bugs that have changed, separate for each repository.
            The positions in the outer list correspond to self.repo_controllers
        """
        bugs_outer = []
        for ctrl in self.repo_controllers:
            bugs = ctrl.get_recent_changes(time_since)
            bugs_outer.append(bugs)
        return bugs_outer
    
    
    def find_associated_bugs(self, modified_bugs):
        """
        Identify versions of the same bug, from different repositories. 
        These bugs need to be merged. 
        
        Identifies known bugs by their bug ID. Unknown (new) bugs are 
        considered to be different versions of the same bug, if they have 
        the same short text (summary).
        
        Arguments
        ---------
        modified_bugs: list[BugData]
            List of modified bugs. 
            
        Returns
        -------
        list[BugMergeTask]
            Tasks for merging bugs (BugMergeTask) 
        
        Notes
        -----
        
        For more flexible text comparison methods see:
        http://stackoverflow.com/questions/682367/good-python-modules-for-fuzzy-string-comparison
        http://stackoverflow.com/questions/145607/text-difference-algorithm
        """
        tasks_known = {} #key is internal bug ID
        bugs_new = []
        #Handle bugs that are already known (synchronized) 
        for bug in modified_bugs:
            #Search for bug with this ID in storage of known bugs.
            repo_name, repo_id = bug.ids.items()[0]
            intl_bug, intl_id = self.known_bug_find(repo_name, repo_id)
            #If bug can't be found it is a new bug.
            if intl_bug is None:
                bugs_new.append(bug)
                continue
            
            #create/append to data for merging known bugs.
            if intl_id in tasks_known:
                task = tasks_known[intl_id]
            else:
                task = BugMergeTask(intl_bug, [])
            task.repo_bugs.append(bug)
            tasks_known[intl_id] = task
            
        #Handle new bugs
        tasks_new = []
        while bugs_new:
            #take new bug, and search for bugs with a matching short text (summary)
            bug = bugs_new.pop()
            matching, no_matching = split(lambda b: b.text_short == bug.text_short, bugs_new)
            #create merge task for current bug and matching bugs
            new_merge = BugMergeTask(None, [bug] + matching)
            tasks_new.append(new_merge)
            #continue working with the remaining bugs
            bugs_new = no_matching
        tasks_new.reverse()
        
        return tasks_known.values() + tasks_new
    
    
    @staticmethod
    def merge_diff3(my_text, old_text, your_text):
        """
        Merge text with external program ``diff3``.
        
        See:
            http://linux.about.com/library/cmd/blcmdl1_diff3.htm
        """
        old_fd, old_name = mkstemp()
        your_fd, your_name = mkstemp()
        my_fd, my_name = mkstemp()
        
        os.write(old_fd, old_text.encode("utf8", errors="replace"))
        os.close(old_fd)
        os.write(your_fd, your_text.encode("utf8", errors="replace"))
        os.close(your_fd)
        os.write(my_fd, my_text.encode("utf8", errors="replace"))
        os.close(my_fd)
        
        args = ["diff3", "-m", "-3", my_name, old_name, your_name] 
        proc = Popen(args, universal_newlines=True, stdout=PIPE) #, stderr=STDOUT)
        merged_text, _ = proc.communicate()
        merged_utext = unicode(merged_text, "utf8", errors="replace")
        
        os.remove(old_name)
        os.remove(your_name)
        os.remove(my_name)
        
        return merged_utext
    
    
    @staticmethod
    def merge_2way(text1, text2):
        """
        Merge two files. Accumulate all text from both files, but don't 
        duplicate common sections.
        """
        diff_lines = difflib.ndiff(text1.split("\n"), text2.split("\n"))
        
        #The interesting lines start with certain strings, collect them
        good_tokens = set(["+ ", "- ", "  "])
        merged_lines = []
        for line in diff_lines:
            if line[:2] in good_tokens:
                merged_lines.append(line[2:])
                
        merged_text = "\n".join(merged_lines)
        return merged_text
    
    
    def merge_bug(self, merge_task):
        """
        Merge several versions of the same bug into one bug.
        """
        assert isinstance(merge_task, BugMergeTask)

        #sort bugs, oldest first
        repo_bugs = sorted(merge_task.repo_bugs, key=lambda b: b.time_modified)
        all_bugs = [merge_task.internal_bug] + repo_bugs \
                   if merge_task.internal_bug else repo_bugs

        #Collect all known IDs of the bug
        ids = {}
        for bug in all_bugs:
            ids.update(bug.ids)

        #Find oldest creation date
        time_created = min([b.time_created for b in all_bugs])
        #Take from youngest bug
        time_modified = repo_bugs[-1].time_modified
        text_short = all_bugs[-1].text_short        
        
        #Merge the long text (bug description)
        if len(repo_bugs) == 1:
            #There is only one modified version of the bug, no need for merging
            text_long = repo_bugs[0].text_long
        elif merge_task.internal_bug:
            #Merge known bug - do repeated 3 way merging
            # - Internal version is common ancestor. 
            # - Versions from repositories are different branches. 
            # - Older branches (bugs) are merged first.
            # - Contents of younger branches (bugs) is preferred in case of 
            #   conflicts.
            base_txt = merge_task.internal_bug.text_long
            other_txt = repo_bugs[0].text_long
            #`my_txt` is preferred in case of conflict
            for bug in repo_bugs[1:]:
                my_txt = bug.text_long
                merged_txt = self.merge_diff3(my_txt, base_txt, other_txt)
                other_txt = merged_txt
            text_long = merged_txt
        else:
            #Merge unknown bug - collect all differences
            merged_txt = repo_bugs[0].text_long
            for bug in repo_bugs[1:]:
                my_txt = bug.text_long
                merged_txt = self.merge_2way(merged_txt, my_txt)
            text_long = merged_txt
        
        #Attributes that are not present in all repositories.
        def last_valid(attr_name):
            """
            Get attribute from youngest bug with a valid attribute.
            
            Bugs can have a special value "*" in certain attributes, which 
            expresses that the attributes is unknown or invalid.
            """
            for bug in reversed(all_bugs):
                attr = getattr(bug, attr_name)
                if attr != "*":
                    return attr
            return "*"        
        
        #Take the youngest valid entry (no "*")
        reporter = last_valid("reporter")
        assigned_to = last_valid("assigned_to")
        status = last_valid("status")
        priority = last_valid("priority")
        resolution = last_valid("resolution")
        kind = last_valid("kind")
        milestone = last_valid("milestone")
        
        #The version of the bug that will be uploaded to all repositories
        merged_bug = BugData(ids=ids, 
                             time_created=time_created,       #administrative
                             time_modified=time_modified, 
                             text_short=text_short,            #text
                             text_long=text_long, 
                             reporter=reporter,                #people
                             assigned_to=assigned_to, 
                             status=status,                    #bug life cycle
                             priority=priority, 
                             resolution=resolution, 
                             kind=kind,
                             milestone=milestone               #grouping
              )
        
        #Find out in which repositories the bug must be created and 
        #in which it must be updated...
        #Find repositories where bug does not exist. (create necessary)
        all_repos = set(self.repo_names)
        bug_exist_in = set(ids.keys())
        not_exist_in = all_repos.difference(bug_exist_in)
        #Find repositories where bug must be updated:
        #In repos without recent changes, but not when we create the bug
        have_changes = set([bug.ids.keys()[0] for bug in repo_bugs])
        bug_diff_in = all_repos.difference(have_changes).difference(not_exist_in)
        #In repos where bug differs to merged bug. 
        for bug in repo_bugs:
            if make_bugs_comparable(bug) != make_bugs_comparable(merged_bug):
                repo = bug.ids.keys()[0]
                bug_diff_in.add(repo)
        
        #Create work parcel for upload algorithm
        write_task = BugWriteTask(bug=merged_bug, 
                                  create_in=list(not_exist_in),
                                  update_in=list(bug_diff_in),
                                  #Create new internal bug if none exists
                                  add_internal=not merge_task.internal_bug)
        return write_task


    def write_bugs(self, write_tasks):
        """
        Upload changed (merged) bugs to the repositories. 
        Store the synchronized bugs also locally.
        """
        #Bugs that should be updated/created in each repository 
        bugs_update = {} # {repo_name:[bug0, bug1, ...]}
        bugs_create = {}
        for ctrl in self.repo_controllers:
            bugs_update[ctrl.repo_name] = []
            bugs_create[ctrl.repo_name] = []
        
        #Distribute the bugs into the repositories' output queue
        for write_task in write_tasks:
            bug = write_task.bug
            for repo_name in write_task.update_in:
                if repo_name == "INTERNAL":
                    continue
                bugs_update[repo_name].append(bug)
            for repo_name in write_task.create_in:
                if repo_name == "INTERNAL":
                    continue
                bugs_create[repo_name].append(bug)
        
        print "Number of bugs to create:"
        for name in self.repo_names:
            print name, ":", len(bugs_create[name])
        print "Number of bugs to update:"
        for name in self.repo_names:
            print name, ":", len(bugs_update[name])
        
        #Upload the bugs to the repositories
        for ctrl in self.repo_controllers:
            repo_name = ctrl.repo_name
            ctrl.update_bugs(bugs_update[repo_name])
            #TODO: better algorithm that relies less on side effects. 
            #      This can not be parallelized at all.
            new_ids = ctrl.create_bugs(bugs_create[repo_name])
            for bug, ID in zip(bugs_create[repo_name], new_ids):
                bug.ids[ctrl.repo_name] = ID
        
        #Update internal state too.
        for task in write_tasks:
            if task.add_internal:
                self.known_bug_add(task.bug)
            else:
                self.known_bug_update(task.bug)


    def synchronize_repos(self, last_sync_time):
        """
        Synchronize all repositories.
        
        Argument
        --------
        last_sync_time: datetime.datetime
            time since which the recent changes are down loaded from 
            the servers.
        
        Returns
        -------
        next_sync_time: datetime.datetime
        known_bugs: list[BugData]
        """
        next_sync_time = datetime.utcnow()
        
        #Download recent changes from bug repositories
        print "Downloading bugs which changed since {t}..." \
              .format(t=last_sync_time)
        changed_bugs = self.get_recent_changes(last_sync_time)
        for repo_name, bugs in zip(self.repo_names, changed_bugs):
            print "    {repo_name}: {n} bugs" \
                  .format(repo_name=repo_name, n=len(bugs))
            
        #Find Different versions of the same bug from different repos
        merge_tasks = self.find_associated_bugs(chain(*changed_bugs)) 
        n_unique = len(merge_tasks)
        n_known = len([True for mtask in merge_tasks if mtask.internal_bug])
        print "Identified {u} unique bugs for merging; {k} known, {n} new." \
              .format(u=n_unique, k=n_known, n=n_unique - n_known)
#        print "merge tasks:"
#        for task in merge_tasks:
#            print task
              
        #Merge different versions into one bug
        write_tasks = [self.merge_bug(mtask) for mtask in merge_tasks]
#        print "write tasks:"
#        for task in write_tasks:
#            if task.create_in:
#                print "CREATE:"
#            print task
        
        #Upload merged bugs to repositories
        print "writing bugs..."
        self.write_bugs(write_tasks)
        print
        
        return next_sync_time, self.known_bugs

