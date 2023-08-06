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
import textwrap
import random
from cPickle import Pickler, Unpickler 
from datetime import datetime
from dateutil import parser as date_parser
from tempfile import mkstemp
from subprocess import Popen, PIPE
from itertools import chain
from collections import Callable
from types import NoneType

import bug_repo_syncer.example_conf
from bug_repo_syncer.repo_io import create_repo_objects, TracController, LpController, \
    RepoControllerDummy, RepoController
from bug_repo_syncer.common import TracData, LaunchpadData, DummyRepoData, \
    BugIntl, KnownBugData, SyncTaskData, BugMergeTask, BugWriteTask, \
    PROGRAM_VERSION_STR, CONF_FORMAT_VERSION, equal_contents, \
    UserFatalError, UnknownWordError, UnknownRepoError, \
    EquivalenceTranslator,  EquivalenceTranslatorNoop, BugLinkTranslator, \
    FilterBase, PeopleMilestoneFilter, BugLinkFilter

class ApplicationMain(object):
    """
    Main object of bug synchronization program 
    """
    def __init__(self, addpw={}): #IGNORE:W0102
        """
        Arguments
        ---------
        
        addpw: dict[str,str]
            Dictionary of additional passwords, useful for testing.
            repository name -> password.
        """
        assert isinstance(addpw, dict)
        
        #name of configuration file
        self.conf_name = "syncer_config.py"
        #name of datafile
        self.data_name = "sync-data.pickle"
        
        #Directory for the configuration file and for the data that the 
        #application saves. 
        self.project_dir = ""
        #The configuration of the repositories
        self.repo_config = SyncTaskData(None, None, None, None, None, None)
        #Additional passwords, useful for test functions
        self.addpw = addpw.copy() 
        
        #Per run information - written at end of run
        #Date and time of last synchronization 
        self.last_sync = datetime(1970, 1, 1)
        #List of known synchronized bugs
        self.known_bugs = []


    def main(self):
        """
        The program's main routine. This function is called by the trivial 
        start script.
        
        This method does not return, it raises a ``SystemExit``! 
        The exit status is 0 if it functions properly, and non-zero otherwise.
        exit status:
            * 1: general error
            * 2: error while parsing the command line
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
                #This is internal error, it should show traceback.
                raise Exception("Unimplemented command: " + cmdinfo.command)
            exit(0)
            
        except UserFatalError as err:
            print "Error: ", err
            print
            exit(1)
        except UnknownRepoError as err:
            print textwrap.dedent(
                """
                Inconsistent repository names.
                
                The people and milestone translators must use the exact same
                repository names, that were used in the description of the
                repositories themselves. All repositories must be mentioned 
                in the translators.
                """).strip()
            print "\nPython says:", err
            

    def parse_args(self, args=None):
        """
        Parse the command line arguments
        
        Argument
        --------
        args: list[str] | None
            The arguments that are parsed. 
            
            ``args`` must exclude the program name; to parse the command line 
            arguments use: ``args=sys.argv[1:]``.
            
            If ``args == None`` the parser parses ``sys.argv``, otherwise 
            it parses args.
            
        Returns
        -------
        The argument parser's result object.
        """
        class VersionLicenseAction(argparse.Action):
            """Show program version and license, then exit"""
            def __call__(self, *args_, **kwargs_):
                progname = os.path.basename(sys.argv[0])
                msg = textwrap.dedent(
                """
                Bug Repo Syncer ({prog}) {vers}
                 
                Copyright (C) 2012 Eike Welk
                https://launchpad.net/bug-repo-syncer
                
                {prog} comes with ABSOLUTELY NO WARRANTY. This is free software,
                and you are welcome to redistribute it under the terms of the 
                GNU General Public License, either version 3 of the License, or 
                any later version.
                """).format(vers=PROGRAM_VERSION_STR, prog=progname)
                print msg
                exit(0)
            
        def date_time(date_str):
            "Parse and validate string that contains date and optionally time."
            try:
                sync_since = date_parser.parse(date_str, yearfirst=True)
            except ValueError, e:
                raise argparse.ArgumentTypeError(str(e))
            if sync_since < datetime(1970, 1, 1):
                raise argparse.ArgumentTypeError(
                                            "dates must be after 1970-01-01.")
            return sync_since
            
        #Create the parser, define error and help messages ---
        parser = argparse.ArgumentParser(
                                    description='Synchronize bug repositories.')
        
        #Define general options
        parser.add_argument(
            "--project-dir", dest="project_dir", action="store", nargs=1, 
            default=None, required=False, metavar="DIRECTORY",
            help="specify directory with configuration and data files")
        parser.add_argument(
            "--version", nargs=0, action=VersionLicenseAction,
            help="show version message and exit")
        
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
        parser_sync.add_argument(
            "--since", dest="time_since", action="store", nargs=1, 
            default=None, required=False, metavar="DATE_TIME", type=date_time,
            help="consider changes since this date (and time)")
        parser_sync.add_argument(
            "--dry-run", dest="dry_run", action="store_true", 
            default=False, required=False, 
            help="don't change the repositories, instead show what the "
                 "program would do")
        
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
        examplepath = bug_repo_syncer.example_conf.__file__.rsplit(".",1)[0] + ".py" 
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
        #TODO: put main parts into function that is called by all commands.
        #      only the printing of information about a working configuration
        #      should remain here.
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
        print "Task:", self.repo_config.task_name
        print "Repositories:",
        for repo in self.repo_config.repos_list:
            print repo.repo_name + ",",
        print 
        print "Known bugs: " + str(len(self.known_bugs))
        print
        
        #Test repositories
        print "Testing repositories..."
        repos_ok = True
        for repo in self.repo_config.repos_list:
            print "Repository:",repo.repo_name
            try:
                create_repo_objects(repo, authenticate=False)
            except Exception as err: #IGNORE:W0703
                print "Error:", err
                repos_ok = False
            print "---"
        print
        if not repos_ok:
            raise UserFatalError("Could not log in to all bug repositories.")
        
        #Directory is read only, synchronization is not possible
        if not ok_dir:
            raise UserFatalError("Project directory is read-only!")
        
    
    
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
        sync_since = self.last_sync
        #React on option "--since"
        if cmdinfo.time_since:
            sync_since = cmdinfo.time_since[0]
        
        #Do synchronization and respect option "--dry-run"
        if cmdinfo.dry_run:
            syncer = RepoSyncer(self.repo_config, self.known_bugs, 
                                      authenticate=False)
            _, _ = syncer.synchronize_repos(sync_since, dry_run=True)
        else:
            syncer = RepoSyncer(self.repo_config, self.known_bugs, 
                                      authenticate=True, 
                                      addpw=self.addpw)
            self.last_sync, self.known_bugs = \
                    syncer.synchronize_repos(sync_since, dry_run=False)

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
            conf_module = self.conf_name.rsplit(".",1)[0] #remove ".py"
            config = __import__(conf_module, globals(), locals(), [], 0)
            sys.path = oldpath
            #Test the file format version
            assert config.FORMAT_VERSION == CONF_FORMAT_VERSION, \
                "The configuration file has the wrong version of the file \n" \
                "format. The required version is: '{}'" \
                .format(CONF_FORMAT_VERSION)
            #Test configuration data
            assert isinstance(config.repo_config, SyncTaskData), \
                "``repo_config`` must be a ``SyncTaskData`` object."
            repo_names = set()
            for rdata in config.repo_config.repos_list:
                #Only known repository descriptions are sensible
                if not isinstance(rdata, (TracData, LaunchpadData, 
                                          DummyRepoData)):
                    raise TypeError("Unknown repository type: \n{r}."
                                    .format(r=repr(rdata)))
                #Repository names must be unique
                if rdata.repo_name in repo_names:
                    raise ValueError("Duplicate repository name: '{n}'." 
                                     .format(n=rdata.repo_name))
                repo_names.add(rdata.repo_name)
            #Get the configuration data
            self.repo_config = config.repo_config
        except Exception, err:
            msg = textwrap.dedent(
                """
                Create a new configuration file with ``bsync init``. This
                will not delete your old configuration file, it will just be 
                renamed to something like:
                
                    "syncer_config.py.2012-03-02 23:16:01.515077"
                
                Convert your old configuration to the new format.
                Good tools for this are ``gvimdiff`` and ``vimdiff``. These
                programs show your new and old configuration file side by
                side, with the differences accented by colors. ``gvimdiff``
                has a GUI and uses the mouse. Start it with:
                
                     ``gvimdiff syncer_config.py syncer_config.py.20*``
                """)
            raise UserFatalError(
                "Broken configuration file!\n\n{err}\n{msg}"
                .format(err=str(err), msg=msg))
        finally:
            #remove project directory from module search path in any case
            sys.path = oldpath 
            
        #Load stored run-to-run data
        dataname = os.path.join(self.project_dir, self.data_name)
        if os.access(dataname, os.R_OK):
            with open(dataname, "rb") as datafile:
                unp = Unpickler(datafile)
                try:
                    self.last_sync = unp.load()
                    self.known_bugs = unp.load()
                except Exception as err:
                    msg = textwrap.dedent(
                    """
                    Broken data file.
                    
                    Error from Unpickler: {e}
                    
                    The data was possibly written by an earlier version of 
                    ``bsync``. If your repositories are nearly perfectly 
                    synchronized, you can simply delete the file and let 
                    ``bsync`` regenerate the information by running:
                        ``bsync sync``
                    
                    If you have however changed bug titles, then only the data 
                    file contains the information which bugs belong together. 
                    In this case you should first synchronize the repositories 
                    with your old version of ``bsync``.
                    """.format(e=repr(err)))
                    raise UserFatalError(msg)


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



class RepoSyncer(object):
    """
    Synchronize two or more repositories. Do all processing that sees bugs as 
    (potentially) different versions of the same bug, that must be merged.
    
    This is the high level interface to the algorithm, and coordinates all 
    other objects.
    
    Steps:
    * Download bugs from repositories. (Mainly handled by ``BugPipeline``.)
    * Identify bugs that belong together. They are different versions of 
      the same bug, and must be merged. -> ``BugMergeTask``
    * Merge different versions of bug. -> ``BugWriteTask``
    * Upload merged bugs to repositories. (Mainly handled by ``BugPipeline``.)
    * Update internal storage of bugs, and relations between them.
    """
    def __init__(self, task_data, synched_bugs=[],                #IGNORE:W0102
                 authenticate=False, addpw={}): 
        """
        Arguments
        ---------
        
        task_data: SyncTaskData
            Configuration information for repositories and translators
            
        synched_bugs: list[BugIntl]
            List of known bugs
            
        authenticate: bool
            If True, access repositories with authentication, 
            if False use anonymous access
            
        addpw: dict[str,str]
            Dictionary of additional passwords, useful for testing.
            repository name -> password.
        """
        assert isinstance(task_data, SyncTaskData)
        assert isinstance(synched_bugs, (list, tuple))
        assert isinstance(authenticate, bool)
        assert isinstance(addpw, dict)
        assert all([isinstance(rdata, (TracData, LaunchpadData, DummyRepoData)) 
                    for rdata in task_data.repos_list])
        
        #Storage of known synchronized bugs: dict[str, KnownBugData]
        self.known_bugs = {}
        for known_bug in synched_bugs:
            intl_id = known_bug.bug.id
            self.known_bugs[intl_id] = known_bug
        #Internal ID is index into ``self.known_bugs``
        self.id_trans = \
            self.create_id_translator(task_data.repos_list, self.known_bugs)
        #Search for additional milestones in the known bugs 
        if task_data.add_unknown_milestones:
            self.discover_milestones(task_data.milestone_translator, 
                                     self.known_bugs.values())
        #Object to translate bug-links in bug descriptions (repo -> internal)
        self.buglink_trans = BugLinkTranslator(self.id_trans) \
                             if task_data.translate_bug_links else None
        
        #Computations that only need to see a single bug are done by BugPipeline
        self.bug_pipelines = []              
        for repo_data in task_data.repos_list:
            #Repository specific objects
            controller, comparator, converter = create_repo_objects(
                                                repo_data, authenticate, addpw)
            #Convert people and milestone names between repositories
            pm_filt = [PeopleMilestoneFilter(repo_data.repo_name, 
                                             task_data.people_translator, 
                                             task_data.milestone_translator, 
                                             task_data.add_unknown_milestones)]
            #Translate bug links in bug descriptions (internal -> repo)
            bl_filt = [BugLinkFilter(repo_data.repo_name, self.id_trans, 
                                     only_intl2repo=True)] \
                      if task_data.translate_bug_links else []
            #Put the components together and also do caching of bugs
            pipe = BugPipeline(controller, comparator, converter, 
                               pm_filt + bl_filt, [])
            self.bug_pipelines.append(pipe)
    

    def _get_repo_controllers(self):
        """
        Return the objects that manage the transmission of bugs over the 
        Internet.
        """
        return [pipe.repo_controller for pipe in self.bug_pipelines]
    repo_controllers = property(_get_repo_controllers)
    
    def _get_repo_names(self):
        """Return list of repositories that are synchronized by this object."""
        return self.id_trans.repo_names[:-1]
    repo_names = property(_get_repo_names)
    
    
    @staticmethod
    def create_id_translator(repo_data_list, known_bugs):
        """Create equivalence translator for bug IDs"""
        assert isinstance(repo_data_list, list)
        assert isinstance(known_bugs, dict)
        
        #Create empty translator
        repos = [repo.repo_name for repo in repo_data_list] + ["INTERNAL"]
        tranlator = EquivalenceTranslator(repos, [])
        
        #fill translator with data from known_bugs
        for intl_id, known_bug in known_bugs.iteritems():
            line = [known_bug.ids[repo] for repo in repos[:-1]] + [intl_id]
            tranlator.add_table_line(line)
            #update the bug's internal ID 
            known_bug.ids["INTERNAL"] = intl_id
            
        return tranlator
    
    
    @staticmethod
    def discover_milestones(translator, known_bugs):
        """
        Put milestones into translator that were not explicitly named by the 
        user.
        
        It is debatable if this function is necessary at all. It helps thinking
        about the algorithm, because it creates a consistent milestone 
        translator. However I'm convinced that the synchronization algorithm
        would work correctly even without this function.
        
        Arguments
        ---------
        translator: EquivalenceTranslatorBase
            The translator to which the milestones are added
        known_bugs: list[BugIntl]
            List of kown bugs, where the milestones are searched.
        """
        for kbd in known_bugs:
            milestone = kbd.bug.milestone
            if milestone is None:
                continue
            try:
                translator.repo2intl("INTERNAL", milestone)
            except UnknownWordError:
                print ("Discovering additional milestone '{}'."
                       .format(milestone))
                translator.add_identity_word(milestone)
                
    
    def create_new_id(self):
        """Create a new bug ID, which is a string of random integer digits."""
        ID_NUM_DIGITS = 6
        ID_CHARS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        while True:
            #Create ID
            digits = []
            for _ in range(ID_NUM_DIGITS):
                digits.append(random.choice(ID_CHARS))
            idstr = "".join(digits)
            #Test if ID already exists
            if idstr not in self.known_bugs:
                return idstr
    
        
    def known_bug_create(self, bug, ids, intl_id=None):
        """
        Add a new bug to the storage for synchronized bugs. 
        Bug gets random ID, unless it is explicitly given with ``intl_id``.
        
        Arguments
        ---------
        bug: BugIntl | NoneType
            The bug that is added to the storage of known bugs.
            Can be None.
            
        ids: dict[str, str]
            IDs that the bug has in the remote repositories.
            
        intl_id: str
            Internal ID that the new bug will get. 
            This is mainly useful for testing. Any 
            If ``intl_id == None`` a random ID is chosen.
        """
        assert isinstance(bug, (BugIntl, NoneType))
        assert isinstance(ids, dict)
        assert isinstance(intl_id, (str, NoneType))
        
        #Put bug into storage
        bug_id = self.create_new_id() if intl_id is None else intl_id
        allids = ids.copy()
        allids.update({"INTERNAL":bug_id})
        if bug is not None:
            bug = bug._replace(repo_name="INTERNAL", id=bug_id)
        kbd = KnownBugData(ids=allids, bug=bug)
        self.known_bugs[bug_id] = kbd
        
        #Create new entry in object to translate bug IDs between repositories
        repos = self.id_trans.repo_names
        line = [ids[repo] for repo in repos[:-1]] + [bug_id]
        self.id_trans.add_table_line(line)
        
        return bug_id


    def known_bug_update(self, bug, ids, intl_id):
        """
        Update bug, or its dictionary of bug IDs, in the storage for 
        synchronized bugs.
        
        Arguments
        ---------
        bug: BugIntl | NoneType
            The bug that is added to the storage of known bugs.
            Can be None.
            
        ids: dict[str, str] | NoneType
            IDs that the bug has in the remote repositories.
            Can be None.
            
        intl_id: str
            Internal ID of the bug that is updated. 
        """
        assert isinstance(bug, (BugIntl, NoneType))
        assert isinstance(ids, (dict, NoneType))
        assert isinstance(intl_id, (str, NoneType))
        
        #Get existing known bug
        try:      
            kbd = self.known_bugs[intl_id]
        except KeyError:
            raise KeyError("Unknown bug ID: {id}".format(id=repr(intl_id)))
        
        #Store new information if given
        bug = bug._replace(repo_name="INTERNAL", id=intl_id) if bug is not None \
              else kbd.bug
        ids = ids if ids is not None else kbd.ids
        kbd = kbd._replace(bug=bug, ids=ids)
        self.known_bugs[intl_id] = kbd
        
        #Create new entry in object to translate bug IDs between repositories
        if ids is not None:
            repos = self.id_trans.repo_names
            line = [ids[repo] for repo in repos[:-1]] + [intl_id]
            self.id_trans.add_table_line(line)


    def known_bug_get(self, bug_id):
        """Return a known bug. Argument ``bug_id`` is the internal ID."""
        try:      
            kbd = self.known_bugs[bug_id]
        except KeyError:
            raise KeyError("Unknown bug ID: {id}".format(id=repr(bug_id)))
        
        return kbd.bug
    
    
    def known_bug_get_ids(self, bug_id):
        """Return the IDs that the bug has in the different repositories."""
        try:      
            kbd = self.known_bugs[bug_id]
        except KeyError:
            raise KeyError("Unknown bug ID: {id}".format(id=repr(bug_id)))
    
        return kbd.ids.copy()
    
    
    def known_bug_find(self, repo_name, bug_id):
        """
        Find a known bug, by the ID it has in one of the repositories.
        
        Returns
        -------
        bug, internal_bug_id
        """
        try:
            intl_id = self.id_trans.repo2intl(repo_name, bug_id)
        except UnknownWordError:
            return None, None
        
        kbd = self.known_bugs[intl_id]
        bug = kbd.bug
        return bug, intl_id
        
        
    def get_recent_changes(self, time_since): 
        """
        Return bugs that changed since a certain date and time.
        
        Arguments
        ---------
        time_since: datetime
        
        Returns
        -------
        list[list[BugIntl]]
            The bugs that have changed, separate for each repository.
            The positions in the outer list correspond to 
            ``self.bug_pipelines`` (or ``self.repo_controllers``)
        """
        bugs_outer = []
        for pipe in self.bug_pipelines:
            bugs = pipe.get_recent_changes(time_since)
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
        modified_bugs: list[BugIntl]
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
            #Search for bug in storage of known bugs. 
            intl_bug, intl_id = self.known_bug_find(bug.repo_name, bug.id)
            #If bug can't be found it is a new bug.
            if intl_bug is None:
                bugs_new.append(bug)
                continue
            
            #find/create task to merge the versions of this bug. 
            if intl_id in tasks_known:
                task = tasks_known[intl_id]
            else:
                task = BugMergeTask(internal_bug=intl_bug, 
                                    internal_id=intl_id,
                                    create_intl=False,
                                    repo_bugs=[])
                tasks_known[intl_id] = task
            #Append bug version to merge task
            task.repo_bugs.append(bug)
            
        #Handle new bugs
        tasks_new = []
        while bugs_new:
            #take new bug, and search for bugs with a matching short text (summary)
            bug = bugs_new.pop(0)
            matching, no_matching = split(
                            lambda b: b.text_short == bug.text_short, bugs_new)
            #create merge task for current bug and matching bugs
            new_merge = BugMergeTask(internal_bug=None,
                                     internal_id=None,
                                     create_intl=True,
                                     repo_bugs=[bug] + matching)
            tasks_new.append(new_merge)
            #continue working with the remaining bugs
            bugs_new = no_matching
        #tasks_new.reverse()
        
        return tasks_known.values(), tasks_new
    
    
    def create_preliminary_bugs(self, merge_tasks):
        """
        Create internal IDs, ID translator entries, and empty ``KnownBugData``
        entries, for new bugs.
        
        This information is used to translate bug links in new bugs.
        
        The method creates ``KnownBugData`` instances with no bug, 
        for all bug merge tasks without internal bug. 
        These empty instances must be replaced by complete ``KnownBugData`` 
        instances in  ``write_bugs``.
                
        An entry (a line) is added to the translator for bug IDs. All IDs that
        are currently unknown are substituted by None.
        """
        new_tasks = []
        for task in merge_tasks:
            assert isinstance(task, BugMergeTask)
            assert (task.internal_bug is None) == task.create_intl
            
            if task.internal_bug is not None:
                continue
            #Collect all known IDs of the bug
            ids = {}
            for bug in task.repo_bugs:
                ids[bug.repo_name] = bug.id
            #Set unknown IDs to None
            for repo in self.repo_names:
                if repo in ids:
                    continue
                ids[repo] = None
            #Create KnowBug and entries in ID translator with these IDs
            intl_id = self.known_bug_create(None, ids)
            #Remember the new internal IDs together with the bugs
            task_new = task._replace(internal_id=intl_id)
            new_tasks.append(task_new)
            
        return new_tasks
    
    
    def translate_bug_links(self, merge_tasks):
        """
        Translate the bug links in all bugs in all tasks.
        """
        translated_tasks = []
        for task in merge_tasks:
            assert isinstance(task, BugMergeTask)
            repo_bugs = []
            for bug in task.repo_bugs:
                trtext = self.buglink_trans.repo2intl(bug.repo_name, 
                                                      bug.text_long)
                trbug = bug._replace(text_long=trtext)
                repo_bugs.append(trbug)
            trtask = task._replace(repo_bugs=repo_bugs)
            translated_tasks.append(trtask)
        
        return translated_tasks
    
    
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
        ids = self.known_bug_get_ids(merge_task.internal_bug.id) \
              if merge_task.internal_bug else {}
        for bug in repo_bugs:
            ids[bug.repo_name] = bug.id
        if merge_task.internal_id is not None:
            ids["INTERNAL"] = merge_task.internal_id

        #Find oldest creation date
        time_created = min([b.time_created for b in all_bugs])
        #Take from youngest bug
        time_modified = repo_bugs[-1].time_modified
        text_short = repo_bugs[-1].text_short        
        
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
        merged_bug = BugIntl(repo_name=None, id=None, 
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
                
        #Create work parcel for upload algorithm
        write_task = BugWriteTask(ids=ids,
                                  bug=merged_bug, 
                                  internal_id=merge_task.internal_id, 
                                  create_intl=merge_task.create_intl)
        return write_task


    def write_bugs(self, write_tasks):
        """
        Upload changed (merged) bugs to the repositories. 
        Store the synchronized bugs also locally.
        """
        all_repos = set(self.repo_names)
        #Bugs that should be created in each repository 
        tasks_create = {}# {repo_name:[task0, task1, ...], ...}
        for name in self.repo_names:
            tasks_create[name] = []
        
        for task in write_tasks:
            #Find repositories where bug does not exist. (create necessary)
            bug_exist_in = set(task.ids.keys())
            not_exist_in = all_repos.difference(bug_exist_in)
            #Distribute the bug into the bug pipelines 
            for pipe in self.bug_pipelines:
                repo_name = pipe.repo_controller.repo_name
                if repo_name in not_exist_in:
                    tasks_create[repo_name].append(task)
                    pipe.queue_create(task.bug)
                else:
                    pipe.queue_update(task.bug, task.ids[repo_name])
        
        #Upload the bugs to the repositories
        for pipe in self.bug_pipelines:
            new_ids = pipe.upload_queued_bugs()
            #Collect the new IDs
            #TODO: better algorithm that relies less on side effects. 
            #      This can not be parallelized at all.
            repo_name = pipe.repo_controller.repo_name
            tasks = tasks_create[repo_name]
            for task, bug_id in zip(tasks, new_ids):
                task.ids[repo_name] = bug_id
 
        #Update internal state too.
        n_up, n_cr = 0, 0
        for task in write_tasks:
            #``KnownBugData`` entries for new bugs were created in 
            #``self.create_preliminary_bugs``
            self.known_bug_update(task.bug, task.ids, task.internal_id)
            if task.create_intl:
                n_cr += 1
            else:
                n_up += 1

        print "{name:20} update:{n_up:4} create:{n_cr:4}".format(
                                        name="INTERNAL", n_up=n_up, n_cr=n_cr)


    def synchronize_repos(self, last_sync_time, dry_run=False):
        """
        Synchronize all repositories.
        
        Argument
        --------
        last_sync_time: datetime.datetime
            Time since which the recent changes are downloaded from 
            the servers.
            
        dry_run: bool
            Don't change the repositories, instead show what would the 
            program upload to the repositories, in the normal case.
            
        Returns
        -------
        next_sync_time: datetime.datetime
        known_bugs: list[BugIntl]
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
        tasks_known, tasks_new = self.find_associated_bugs(chain(*changed_bugs)) 
        n_new = len(tasks_new)
        n_known = len(tasks_known)
        print "Identified {u} unique bugs for merging; {k} known, {n} new." \
              .format(u=n_known + n_new, k=n_known, n=n_new)
#        print "merge tasks:"
#        for task in merge_tasks:
#            print task
        
        #Create internal IDs for the new bugs
        tasks_new1 = self.create_preliminary_bugs(tasks_new)
        
        #Translate bug links ("bug #123") to internal format
        merge_tasks = self.translate_bug_links(tasks_known + tasks_new1) \
                      if self.buglink_trans else tasks_known + tasks_new1
        
        #Merge different versions into one bug
        write_tasks = [self.merge_bug(mtask) for mtask in merge_tasks]
#        print "write tasks:"
#        for task in write_tasks:
#            if task.create_in:
#                print "CREATE:"
#            print task
        
        #Upload merged bugs to repositories
        if not dry_run:
            print "uploading bugs..."
            self.write_bugs(write_tasks)
        else:
            print "Tasks to change the repositories: \n"
            for task in write_tasks:
                print task.fancy_str()
            next_sync_time = last_sync_time
        
        return next_sync_time, self.known_bugs.values()



class BugPipeline(object):
    """
    Coordinate handling of individual bug versions: uploading, downloading,
    various translation steps, caching of downloaded bugs, queuing of bugs 
    for upload. 
    """
    def __init__(self, repo_controller, bugs_equal_contents,      #IGNORE:W0102
                 repo_filter, filters=[], cached_bugs=[]):
        """
        Arguments
        ---------
        repo_controller: RepoController
            Transfer bugs to/from a repository overt the Internet.
            
        bugs_equal_contents: Callable
            Function with two arguments. It returns True whe two bugs have the
            same contents, and False otherwise. The function must ignore the
            attributes: "repo_name", "id", "time_created", "time_modified".
            
        repo_filter: 
            Convert bugs to/from repository specific format and internal format.
            
        filters: list[FilterBase]
            Translate certain aspects of the bug, for example the names of 
            people.
            
        cached_bugs: list[repository specific bug data]
            Bugs that have been downloaded from the repository.
        """
        assert isinstance(repo_controller, RepoController)
        assert isinstance(bugs_equal_contents, Callable)
        assert isinstance(repo_filter, FilterBase)
        
        self.repo_controller = repo_controller
        self.bugs_equal_contents = bugs_equal_contents
        self.repo_filter = repo_filter
        self.filters = filters[:]
        #dict[bug ID -> bug]; bugs that have been downloaded.
        self.dl_cache = {}
        for bug in cached_bugs:
            self.dl_cache[bug.id] = bug
        #Queue for bugs that will be updated, and their IDs
        self.up_bugs = []
        self.up_ids = []
        #Queue for bugs that will be created
        self.cr_bugs = []
    
    
    def get_recent_changes(self, time_since): 
        """
        Return list of bugs that changed since a certain date and time.
        
        Download the bugs from the repository, perform the translation steps,
        and store the raw downloaded bugs.  
        """
        repo_bugs = self.repo_controller.get_recent_changes(time_since)
        #put raw bugs into cache
        self.dl_cache.clear()
        for bug in repo_bugs:
            self.dl_cache[bug.id] = bug
        #perform all format conversions and translations
        intl_bugs = [self.filter_repo2intl(bug) for bug in repo_bugs]
        return intl_bugs
        
        
    def queue_create(self, bug):
        """
        Queue a bug that should be created in the repository later.
        #TODO: design: communication of new bug IDs to the storage of 
               known bugs. This should even work when the upload is done in a 
               separate thread.
        """
        filtbug = self.filter_intl2repo(bug)
        self.cr_bugs.append(filtbug)
        
        
    def queue_update(self, bug, bug_id):
        """
        Queue a bug that should be updated in the repository later.
        """
        filtbug = self.filter_intl2repo(bug)
        #don't upload if there was no change.
        if bug_id in self.dl_cache:
            cachebug = self.dl_cache[bug_id]
            if self.bugs_equal_contents(filtbug, cachebug):
                return
        self.up_bugs.append(filtbug)
        self.up_ids.append(bug_id)
    
          
    def upload_queued_bugs(self):
        """
        Upload queued bugs to the repository, return IDs of created bugs.
        """
        print "{name:20} update:{n_up:4} create:{n_cr:4}".format(
                                name=self.repo_controller.repo_name, 
                                n_up=len(self.up_bugs), n_cr=len(self.cr_bugs))
        
        self.repo_controller.update_bugs(self.up_bugs, self.up_ids)
        del self.up_bugs[:]
        del self.up_ids[:]
        crids = self.repo_controller.create_bugs(self.cr_bugs)
        del self.cr_bugs[:]
        return crids
    
    
    def filter_repo2intl(self, bug):
        """
        Do all filtering operations from the repository specific format 
        to the internal format.
        """
        fbug = self.repo_filter.repo2intl(bug)
        for filter_ in self.filters:
            fbug = filter_.repo2intl(fbug)
        return fbug
        
        
    def filter_intl2repo(self, bug):
        """
        Do all filtering operations from the internal format to the 
        repository specific format.
        """
        fbug = bug
        for filter_ in reversed(self.filters):
            fbug = filter_.intl2repo(fbug)
        rbug = self.repo_filter.intl2repo(fbug)
        return rbug
 
