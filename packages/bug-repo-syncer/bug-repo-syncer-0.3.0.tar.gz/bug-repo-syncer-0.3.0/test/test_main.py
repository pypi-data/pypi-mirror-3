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
Tests for module main
"""
#pylint: disable=W0212,E1101

from __future__ import division
from __future__ import absolute_import

import pytest #contains `skip`, `fail`, `raises`, `config`

import os
import sys
import stat
import shutil
import textwrap
from pprint import pprint
from datetime import datetime
from time import sleep, clock
from subprocess import call

#from test.helpers import make_bugs_comparable

import bug_repo_syncer.example_conf as example_conf
from bug_repo_syncer.common import DummyRepoData, SyncTaskData, \
    BugIntl, KnownBugData, \
    BugMergeTask, BugWriteTask, equal_contents, \
    EquivalenceTranslatorNoop, EquivalenceTranslator, UserFatalError, \
    FilterBase, FilterNoop, PeopleMilestoneFilter
from bug_repo_syncer.repo_io import create_repo_objects, \
    RepoControllerDummy, TracController, BugTracFilter, bugtrac_equal_contents
    
from bug_repo_syncer.main import RepoSyncer, ApplicationMain, BugPipeline



#---------------------- Test ApplicationMain -------------------------------
#==========================================================================

def test_start_script():
    """
    Test the start script. 
    
    Execute the ``init`` sub-command, which always succeeds when the 
    directory is writable.
    """
    #Set up directory names and remove the test directory
    old_cwd = os.getcwd()
    _tmp_dir, proj_dir, _conf_file = setup_test_resources("test_start_script")
    #create test directory and go there
    os.mkdir(proj_dir)
    os.chdir(proj_dir)
    
    #call the init script
#    assert call("ls ../../../", shell=True) == 0
    assert call("../../../bsync init", shell=True) == 0
    
    os.chdir(old_cwd)
    
    
#---------------------- Test ApplicationMain -------------------------------
#==========================================================================

def test_ApplicationMain__parse_args():
    """Test the parser for the command line arguments."""
    app = ApplicationMain()
    
    #command init
    pargs = app.parse_args("init".split())
    print pargs
    assert pargs.command == "init"

    #command stat + --project-dir
    pargs = app.parse_args("info".split())
    print pargs
    assert pargs.command == "info"

    #command sync
    pargs = app.parse_args("sync".split())
    print pargs
    assert pargs.command == "sync"
        
    #option --project-dir + stat
    pargs = app.parse_args("--project-dir=foo/bar info".split())
    print pargs
    assert pargs.project_dir[0] == "foo/bar"
    assert pargs.command == "info"
    #no option
    pargs = app.parse_args("info".split())
    print pargs
    assert pargs.project_dir == None
        
    #Produce version info
    print
    with pytest.raises(SystemExit):
        pargs = app.parse_args("--version".split())
        
    #Produce help message
    print
    with pytest.raises(SystemExit):
        pargs = app.parse_args("--help".split())
    


def setup_test_resources(testname):
    """
    Set up path names and remove the test directory.
    
    Argument
    -------- 
    testname
        name of project directory
        
    Returns
    ------- 
    tmp_dir
        absolute path of test root directory, ``proj_dir`` will be created there
    proj_dir
        absolute path of project directory, ``conf_file`` will be created there
    conf_file
        absolute path of configuration file for ``bsync`` program
    """
    tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
    proj_dir = os.path.join(tmp_dir, testname)
    conf_file = os.path.join(proj_dir, "syncer_config.py")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    if os.path.exists(proj_dir):
        print "Removing:", proj_dir
        os.chmod(proj_dir, stat.S_IRWXU)
        shutil.rmtree(proj_dir)
    return tmp_dir, proj_dir, conf_file

def call_application_main(arg_str):
    """
    Create application and call its main function. 
    Return the program's return code.
    """
    app = ApplicationMain()
    sys.argv = arg_str.split()
    try:
        app.main()
    except SystemExit, e:
        return str(e)
    else:
        assert False, "Must raise SystemExit"
    
    
def test_ApplicationMain__main__version_help():
    """
    Test the application's ``--version`` and ``--help`` options. 
    Only test that options exist, and don't lead to crashes.
    (You can check the messages this way too, off course.)
    """        
    print "Version info ------------------------------------------------------"
    assert call_application_main("bsync --version") == "0"
    print "Help text ---------------------------------------------------------"
    assert call_application_main("bsync --help") == "0"
    #non existing options must result in error
    print "Command line parse error ------------------------------------------"
    assert call_application_main("bsync --nonsense") == "2"

    

def test_ApplicationMain__main__info():
    """
    Test the application's ``info`` command. 
    In case of errors it exits with status 1.
    """
    #Set up directory names and remove the test directory
    old_cwd = os.getcwd()
    tmp_dir, proj_dir, conf_file = setup_test_resources("main_info")
    
    print "Project directory does not exist ----------------------------------"
    os.chdir(tmp_dir)
    assert call_application_main(
                        "bsync --project-dir {} info".format(proj_dir)) == "1"
    
    print "Project directory is empty ----------------------------------------"
    os.mkdir(proj_dir)
    assert call_application_main(
                        "bsync --project-dir {} info".format(proj_dir)) == "1"
    os.chdir(proj_dir)
    assert call_application_main("bsync info") == "1"
    
    print "Broken configuration file -----------------------------------------"
    #because of import caching this test must come before a  functioning 
    #configuration module is imported.
    with open(conf_file, "w") as f:
        f.write("Broken configuration file.")
        f.close()
    assert call_application_main("bsync info") == "1"

    print "Configuration file exists (OK) ------------------------------------"
    example_conf_py = example_conf.__file__.rsplit(".",1)[0] + ".py"
    shutil.copy(example_conf_py, conf_file)
    assert call_application_main("bsync info") == "0"
    
    print "Project dir is read only ------------------------------------------"
    os.chmod(proj_dir, stat.S_IRUSR | stat.S_IEXEC)
    assert call_application_main("bsync info") == "1"
    os.chmod(proj_dir, stat.S_IRWXU)
    
    print "Broken data file --------------------------------------------------"
    #Copy broken data file into project directory
    join = os.path.join
    shutil.copy(join(tmp_dir, "..", "data", "sync-data.pickle.1.broken"), 
                join(proj_dir, "sync-data.pickle"))
    assert call_application_main("bsync info") == "1"
    
    #restore original working directory
    os.chdir(old_cwd)
    print "finished"
    
    
    
def test_ApplicationMain__main__init():
    """
    Test the application's ``init`` command. 
    In case of errors it exits with status 1.
    """
    #Set up directory names and remove the test directory
    old_cwd = os.getcwd()
    tmp_dir, proj_dir, conf_file = setup_test_resources("main_init")
    
    print "Project directory does not exist ----------------------------------"
    os.chdir(tmp_dir)
    assert call_application_main(
                        "bsync --project-dir {} init".format(proj_dir)) == "1"
        
    print "project dir is read only  -----------------------------------------"
    os.mkdir(proj_dir)
    os.chdir(proj_dir)
    os.chmod(proj_dir, stat.S_IRUSR | stat.S_IEXEC)
    assert call_application_main("bsync init") == "1"
    os.chmod(proj_dir, stat.S_IRWXU)
    
    print "Project directory is rw (OK) --------------------------------------"
    assert call_application_main("bsync init") == "0"
    assert os.path.exists(conf_file)
    #``info`` must confirm that configuration is working
    assert call_application_main("bsync info") == "0"
    
    print "Configuration file exists  ---------------------------------------"
    #Must create new configuration file, and rename old configuration file.
    assert call_application_main("bsync init") == "0"
    #find old config file, it has current time and date appended, for example:
    #    "syncer_config.py.2012-03-02 20:21:59.827151"
    proj_files = os.listdir(proj_dir)
    print proj_files
    for pfile in proj_files:
        if pfile.startswith("syncer_config.py.20"):
            break
    else:
        assert False, "Old configuration file not found."
    
    #restore original working directory
    os.chdir(old_cwd)
    print "finished"
        


def test_ApplicationMain__main__sync_errors():
    """
    Test the application's ``sync`` command, but only errors. 
    Real synchronization is handled separately.
    In case of errors it exits with status 1.
    """
    #Set up directory names and remove the test directory
    old_cwd = os.getcwd()
    tmp_dir, proj_dir, _ = setup_test_resources("main_sync_errors")
    
    print "Project directory does not exist ----------------------------------"
    os.chdir(tmp_dir)
    assert call_application_main(
                        "bsync --project-dir {} sync".format(proj_dir)) == "1"
        
    print "configuration file does not exist ---------------------------------"
    os.mkdir(proj_dir)
    os.chdir(proj_dir)
    assert call_application_main("bsync sync") == "1"
    
    #create working configuration
    assert call_application_main("bsync init") == "0"
    #``info`` must confirm that configuration is working
    assert call_application_main("bsync info") == "0"
    
    print "project dir is read only  -----------------------------------------"
    os.chmod(proj_dir, stat.S_IRUSR | stat.S_IEXEC)
    assert call_application_main("bsync sync") == "1"
    os.chmod(proj_dir, stat.S_IRWXU)
    
    print "bad date in option ``--since`` must return orderly with system exit"
    print "Nonsense date:"
    assert call_application_main("bsync sync --since 2012-13-14") == "2"
    print "Date too early:"
    assert call_application_main("bsync sync --since 1910-01-01") == "2"
    
    print 
    #restore original working directory
    os.chdir(old_cwd)
    print "finished"
        


def test_ApplicationMain__read_data():
    """
    Test the reading the programs data file.
    * Reading broken configuration file must produce error message 
      (not traceback).
    * Write and read working data (really no stored bugs)
    """
    #Set up empty project directory, and go into it
    tmp_dir, proj_dir, conf_file = setup_test_resources("read_data")
    os.mkdir(proj_dir)
    old_cwd = os.getcwd()
    os.chdir(proj_dir)
    
    join = os.path.join
    #Copy working configuration file into project directory
    example_conf_py = example_conf.__file__.rsplit(".",1)[0] + ".py"
    shutil.copy(example_conf_py, conf_file)    
    #Copy broken data file into project directory
    shutil.copy(join(tmp_dir, "..", "data", "sync-data.pickle.1.broken"), 
                join(proj_dir, "sync-data.pickle"))
    
    #try to read the broken data
    app = ApplicationMain()
    with pytest.raises(UserFatalError):
        app.read_data()
    
    #write an empty data file and read it
    app.write_data()
    app.read_data()
    
    #restore original working directory
    os.chdir(old_cwd)
    print "finished"
    
    

#---------------------- Test RepoSyncer -------------------------------
#==========================================================================

def make_dummy_task():
    """Create working SyncTaskData with dummy objects."""
    task = SyncTaskData(task_name="test", 
                        repos_list=[DummyRepoData(repo_name="repo_a", 
                                                  initial_bugs=[]), 
                                    DummyRepoData(repo_name="repo_b", 
                                                  initial_bugs=[])], 
                        people_translator=EquivalenceTranslatorNoop(), 
                        milestone_translator=EquivalenceTranslatorNoop(),
                        add_unknown_milestones=True,
                        translate_bug_links=True)
    return task


def make_bugs():
    """Create bugs, that match the dummy task"""
    bug0 =  BugIntl(repo_name= "repo_a", id="a0",
                    time_created=datetime(2000, 1, 1),
                    time_modified=datetime(2000, 2, 1),
                    text_short=u"test bug zero",
                    text_long=u"Description of bug zero.",
                    reporter="eike", assigned_to="eike",
                    status="new", priority="minor", resolution="none", kind="defect",
                    milestone="1.0.0")
    bug1 =  BugIntl(repo_name= "repo_a", id="a1",
                    time_created=datetime(2000, 1, 1),
                    time_modified=datetime(2000, 2, 2),
                    text_short=u"test bug one",
                    text_long=u"Description of bug one.",
                    reporter="eike", assigned_to=None,
                    status="new", priority="minor", resolution="none", kind="defect",
                    milestone=None)
    return [bug0, bug1]


def make_known_bugs():
    """Create known bugs for a syncer object"""
    bug0, bug1 = make_bugs()
    bug0 = bug0._replace(repo_name= "INTERNAL", id="000000",)
    bug1 = bug1._replace(repo_name= "INTERNAL", id="000001",)
    kbd0 = KnownBugData({"repo_a":"a0", "repo_b":"b0"}, bug0)
    kbd1 = KnownBugData({"repo_a":"a1", "repo_b":"b1"}, bug1)
    return [kbd0, kbd1]
    


def test_RepoSyncer__creation(): 
    """RepoSyncer: creation"""
    #test dummy data
    dummy_task = make_dummy_task()
    RepoSyncer(dummy_task, [])    
    
    #Login into real repositories
    RepoSyncer(example_conf.repo_config, [])

    #Get known bugs. Their IDs are all previously known
    kbd0, kbd1 = make_known_bugs()
    bug0, bug1 = kbd0.bug, kbd1.bug
    print "bug0:", kbd0.ids
    print "bug1:", kbd1.ids
    #Create synchronization object with two known bugs
    sync = RepoSyncer(dummy_task, [kbd0, kbd1])
    #Get bug by its internal ID
    assert bug0 == sync.known_bug_get("000000")
    assert bug1 == sync.known_bug_get("000001")
    #Get bug by the ID that it has in a remote repository 
    bug0a, _ = sync.known_bug_find("repo_a", "a0")
    bug1a, _ = sync.known_bug_find("repo_a", "a1")
    assert bug0 == bug0a
    assert bug1 == bug1a
    
    #Error: Unknown repository type
    err_task = dummy_task._replace(repos_list=["repo_a", "repo_b"])
    with pytest.raises(AssertionError):
        RepoSyncer(err_task, [])



def test_RepoSyncer__create_id_translator():
    task = make_dummy_task()    
    synched_bugs = make_known_bugs()
    #We need dict[ID -> KnownBugData]
    #A few lines from RepoSyncer.__init__
    known_bugs = {}
    for kbd in synched_bugs:
        intl_id = kbd.bug.id #IGNORE:E1103
        known_bugs[intl_id] = kbd
    
    translator = RepoSyncer.create_id_translator(task.repos_list,
                                                       known_bugs)
    
    assert isinstance(translator, EquivalenceTranslator)
    assert translator.repo2intl("repo_a", "a0") == "000000"
    assert translator.repo2intl("repo_b", "b0") == "000000"
    assert translator.repo2intl("repo_a", "a1") == "000001"
    assert translator.repo2intl("repo_b", "b1") == "000001"



def test_RepoSyncer__discover_milestones():
    #Create task with milestone translator that knows no milestone
    task = make_dummy_task()    
    miletr = EquivalenceTranslator(repos="repo_a, repo_b, INTERNAL", vals="")
    task = task._replace(milestone_translator=miletr)
    #create two bugs - bug 0 has milestone "1.0.0"
    synched_bugs = make_known_bugs()
    assert synched_bugs[0].bug.milestone == "1.0.0"
    
    #Create synchronization object - discover milestone "1.0.0"
    _sync = RepoSyncer(task, synched_bugs)
    
    #Find milestone in updated translator - it is translated into itself
    assert miletr.intl2repo("repo_a", "1.0.0") == "1.0.0"



def test_RepoSyncer__create_new_id():
    """Test creation of new IDs, which are strings of random integer digits."""
    #Create synchronization object
    dummy_task = make_dummy_task()
    sync = RepoSyncer(dummy_task, [])
    
    n_ids = 10
    ids = set()
    n_digits = None
    #Create some IDS
    for i in range(n_ids):
        idstr = sync.create_new_id()
        print idstr
        #must consist of random integer digits
        assert idstr.isdigit() 
        #All IDs must have the same length
        if i == 0:
            n_digits = len(idstr)
        assert len(idstr) == n_digits
        
        ids.add(idstr)
        
    #This is likely to fail for bigger numbers of n_ids
    #This test will sporadically fail
    assert len(ids) == n_ids
    
    
    
def test_RepoSyncer__add_known_bug():
    """Add a known bug to the storage of known bugs."""
    #Create synchronization object with two repositories and no known bugs.
    task_data = make_dummy_task()  
    sync = RepoSyncer(task_data, [])
    
    #Create some bugs 
    bug0, bug1 = make_bugs()

    #put the bugs into the storage of known bugs
    id0 = sync.known_bug_create(bug0, {"repo_a":"a0", "repo_b":"b0"})
    id1 = sync.known_bug_create(bug1, {"repo_a":"a1", "repo_b":"b1"})
    
    assert len(sync.known_bugs) == 2
    assert equal_contents(sync.known_bug_get(id0), bug0)
    assert equal_contents(sync.known_bug_get(id1), bug1)
    bug0a, _ = sync.known_bug_find("repo_a", "a0")
    assert equal_contents(bug0a, bug0)
    bug0b, _ = sync.known_bug_find("repo_b", "b0")
    assert equal_contents(bug0b, bug0)
    
    print "finished ...add_known_bug"
    
    

def test_RepoSyncer__known_bug_update():
    #Create synchronization object with two repositories and some known bugs.
    task_data = make_dummy_task()
    kbd0, kbd1 = make_known_bugs()
    sync = RepoSyncer(task_data, [kbd0, kbd1])
    
    #Create some modified bugs.
    #get data from the known bugs
    bug0, id0 = kbd0.bug, kbd0.bug.id
    bug1, id1 = kbd1.bug, kbd1.bug.id
    #modify them
    bug0m = bug0._replace(text_short="Modified 0")
    bug1m = bug1._replace(text_short="Modified 1")
    
    #test: update bugs
    sync.known_bug_update(bug0m, None, id0)
    sync.known_bug_update(bug1m, None, id1)
    #The bugs need to be modified
    assert sync.known_bug_get(id0) == bug0m
    assert sync.known_bug_get(id1) == bug1m
    
    #Create dictionary of bug IDs
    idsm = {"repo_a":"000", "repo_b":"b0"}
    
    #test: update bug IDs
    sync.known_bug_update(None, idsm, id0)
    #The IDs must be modified
    assert sync.known_bug_get_ids(id0) == idsm
    #The ID translator must be modified too
    assert sync.id_trans.intl2repo("repo_a", id0) == "000"
    assert sync.id_trans.repo2intl("repo_a", "000") == id0
    
    print "finished ...known_bug_update"
    
    
    
def test_RepoSyncer__known_bug_find():
    #Create synchronization object with two repositories and some known bugs.
    task_data = make_dummy_task()    
    kbd0, kbd1 = make_known_bugs()
    bug0, bug1 = kbd0.bug, kbd1.bug
    sync = RepoSyncer(task_data, [kbd0, kbd1])
    
    #test: find bugs in internal storage
    #under their IDs on "repo_a"
    bug0a, id0a = sync.known_bug_find("repo_a", "a0")
    bug1a, id1a = sync.known_bug_find("repo_a", "a1")
    #under their IDs on "repo_b"
    bug0b, id0b = sync.known_bug_find("repo_b", "b0")
    bug1b, id1b = sync.known_bug_find("repo_b", "b1")
    
    assert bug0a == bug0b
    assert id0a == id0b
    assert equal_contents(bug0, bug0a) 
    assert equal_contents(bug0, bug0b)
    
    assert bug1a == bug1b
    assert id1a == id1b
    assert equal_contents(bug1, bug1a) 
    assert equal_contents(bug1, bug1b)
    
    print "finished ...known_bug_find"



def test_RepoSyncer__get_recent_changes():
    #Create synchronization object with two repositories.
    task_data = make_dummy_task()    
    sync = RepoSyncer(task_data, [])
    repo_a, repo_b = sync.repo_controllers
    
    #The repositories should contain bugs
    bug1, bug2 = make_bugs()
    repo_a.create_bugs([bug1, bug2])
    repo_b.create_bugs([bug1])

    bugs_list_list = sync.get_recent_changes(datetime(1970, 1, 1))
    
    assert len(bugs_list_list) == 2
    assert len(bugs_list_list[0]) == 2
    assert len(bugs_list_list[1]) == 1
    
    
    
def test_RepoSyncer__find_associated_bugs():
    #Create synchronization object with two repositories and some known bugs.
    task_data = make_dummy_task()    
    synched_bugs = make_known_bugs()
    sync = RepoSyncer(task_data, synched_bugs)
    
    #Create some modified bugs that we got from the repositories.
    bug0, bug1 = make_bugs()
    
    #Known bugs
    bug0a = bug0._replace(repo_name="repo_a", id="a0") #bug0, repo a
    bug0b = bug0._replace(repo_name="repo_b", id="b0") #bug0, repo b
    bug1a = bug1._replace(repo_name="repo_a", id="a1") #bug1, repo a
    #New bugs
    bug3a = bug0._replace(repo_name="repo_a", id="a3", text_short="the third bug.")
    bug3b = bug0._replace(repo_name="repo_b", id="b3", text_short="the third bug.")
    bug4a = bug0._replace(repo_name="repo_a", id="a4", text_short="the fourth bug.")
    
    tasks_known, tasks_new = sync.find_associated_bugs(
                                    [bug0a, bug0b, bug1a, bug3a, bug3b, bug4a])
    print "Known bugs:"
    pprint(tasks_known)
    print "New bugs:"
    pprint(tasks_new)
        
    assert len(tasks_known) == 2
    assert len(tasks_new) == 2
    #TODO: more assertions 



def test_RepoSyncer_create_preliminary_bugs():
    """Test: RepoSyncer.create_preliminary_bugs"""
    #Create synchronization object with two repositories.
    task_data = make_dummy_task()    
    sync = RepoSyncer(task_data)
    
    #Create some a bug that we got from the repositories.
    bug0, _ = make_bugs()
    #Create merge task for new bug
    task0 = BugMergeTask(internal_bug=None, 
                         repo_bugs=[bug0], 
                         internal_id=None, 
                         create_intl=True)
    
    #The test: create internal ID for the new bug
    task0m, = sync.create_preliminary_bugs([task0])
    
    #The new ID must be in the task 
    assert task0m.internal_id is not None
    #It must be possible to translate the bug ID now
    intl_id = sync.id_trans.repo2intl(bug0.repo_name, bug0.id)
    assert intl_id == task0m.internal_id
    repo_id = sync.id_trans.intl2repo(bug0.repo_name, intl_id)
    assert repo_id == bug0.id
    
    print "task0 :", task0
    print "task0m:", task0m
    print "sync.known_bugs:", sync.known_bugs



def test_RepoSyncer_translate_bug_links():
    """Test: RepoSyncer.translate_bug_links"""
    #Create synchronization object with two repositories.
    task_data = make_dummy_task()    
    synched_bugs = make_known_bugs()
    sync = RepoSyncer(task_data, synched_bugs)
    
    #Create known bug that we got from the repositories.
    bug0, _ = make_bugs()
    bug0 = bug0._replace(text_long="A link to bug #a1 is in this text.")
    #Create merge task - 
    #inconsistent for known bug, but ``translate_bug_links`` doesn't care
    task0 = BugMergeTask(internal_bug=None, 
                         repo_bugs=[bug0], 
                         internal_id=None, 
                         create_intl=True)
    
    #The test
    task0m, = sync.translate_bug_links([task0])
    
    #The description must contain the translated bug link
    bug0tr = task0m.repo_bugs[0]
    assert bug0tr.text_long.find("bug #000001") != -1
    
    print "task0 :", task0
    print "task0m:", task0m



def test_RepoSyncer__merge_diff3():
    """Three way merge function, that calls external program"""
    text0 = \
"""
These lines are the same in all versions of the text.  
File 0 is considered the base file, files 1 and 2 are from different branches.
This text exists only in file number 0. (deleted line)
One more common block of text, which may be a separate 
block of text. Some more text.
An other common line. (Number five)
An other common line. (Number six)
An other common line. (Number seven)
A line which conflicts in all files. (file 0)
An other common line. (Number eight)
An other common line. (Number nine)
An other common line. (Number ten)
"""

    text1 = \
"""
These lines are the same in all versions of the text.  
File 0 is considered the base file, files 1 and 2 are from different branches.
One more common block of text, which may be a separate 
block of text. Some more text.
This line exists only in file number 1.
An other common line. (Number five)
An other common line. (Number six)
This line conflicts in files 1 and 2. (file 1)
An other common line. (Number seven)
This line conflicts in all files. (file 1)
An other common line. (Number eight)
An other common line. (Number nine)
An other common line. (Number ten)
"""

    text2 = \
"""
These lines are the same in all versions of the text.  
File 0 is considered the base file, files 1 and 2 are from different branches.
One more common block of text, which may be a separate 
block of text. Some more text.
An other common line. (Number five)
This line exists only in file number 2.
An other common line. (Number six)
Conflicting line in files 1 and 2. (file 2)
An other common line. (Number seven)
Conflicting line in all files. (file 2)
An other common line. (Number eight)
An other common line. (Number nine)
An other common line. (Number ten)
"""
    
    merged_text = RepoSyncer.merge_diff3(text2, text0, text1)

    print merged_text
    #TODO: test for the expected output.



def test_RepoSyncer__merge_2way():
    """Three way merge function, that calls external program"""
    text1 = \
"""
These lines are the same in all versions of the text.
File 0 is considered the base file, files 1 and 2 are from different branches.
One more common block of text, which may be a separate
block of text. Some more text.
This line exists only in file number 1.
An other common line. (Number five)
An other common line. (Number six)
This line conflicts in files 1 and 2. (file 1)
An other common line. (Number seven)
This line conflicts in all files. (file 1)
An other common line. (Number eight)
An other common line. (Number nine)
An other common line. (Number ten)
""".strip()

    text2 = \
"""
These lines are the same in all versions of the text.
File 0 is considered the base file, files 1 and 2 are from different branches.
One more common block of text, which may be a separate
block of text. Some more text.
An other common line. (Number five)
This line exists only in file number 2.
An other common line. (Number six)
Conflicting line in files 1 and 2. (file 2)
An other common line. (Number seven)
Conflicting line in all files. (file 2)
An other common line. (Number eight)
An other common line. (Number nine)
An other common line. (Number ten)
""".strip()
    
    #The test
    merged_text = RepoSyncer.merge_2way(text1, text2)
    print merged_text
    
    #The merged text must contain all lines from both versions
    all_lines = set(text1.split("\n")) | set(text2.split("\n"))
    merged_lines = set(merged_text.split("\n"))
    assert  merged_lines == all_lines
    #The merged text must not contain any duplicate lines.
    assert len(all_lines) == len(merged_text.split("\n"))
  


def test_RepoSyncer__merge_bugs():
    """
    Test merging different versions of a bug (bugs from different repositories.
    """
    #Create synchronization object with two repositories.
    task_data = make_dummy_task()    
    sync = RepoSyncer(task_data, [])

    #Create some bugs:
    # * bug1:         internal bug from ``synched_bugs``. 
    # * bug1a, bug1b: modified versions of bug1, from the repositories.
    # * bug3a, bug3b: two versions of a bug, that is not stored in ``synched_bugs``.
    bug1, _ = make_bugs()
    id1 = sync.known_bug_create(bug1, {"repo_a":"a1", "repo_b":"b1"})
    bug1 = sync.known_bug_get(id1)
    #Known bugs
    bug1a = bug1._replace(repo_name="repo_a", id="a1", 
                          time_modified=datetime(2000, 3, 1),
                          text_long="Description of bug one.\n"
                                    "Addition from repo_a\n", 
                          status="confirmed", priority="major",) #bug1, repo a
    bug1b = bug1._replace(repo_name="repo_b", id="b1", 
                          time_modified=datetime(2000, 3, 2),
                          text_long="Description of bug one.\n"
                                    "Addition from repo_b\n", 
                          status="in_progress", priority="*",) #bug1, repo b
    #New bugs
    bug3a = bug1._replace(repo_name="repo_a", id="a3", 
                          time_modified=datetime(2000, 3, 1), 
                          text_short="the third bug.",
                          text_long="Description of bug 3 from repo_a", 
                          status="confirmed", priority="major",)
    bug3b = bug1._replace(repo_name="repo_b", id="b3", 
                          time_modified=datetime(2000, 3, 2), 
                          text_short="the third bug.",
                          text_long="Description of bug 3 from repo_b", 
                          status="in_progress", priority="*",)
    
    #Tasks to merge the contents of certain bugs
    merge_task_known_2 = BugMergeTask(bug1, [bug1a, bug1b], bug1.id, False) #known bug
    merge_task_known_1 = BugMergeTask(bug1, [bug1a], bug1.id, False)        #known bug
    merge_task_new_2 =   BugMergeTask(None, [bug3a, bug3b], None, True) #new bug
    merge_task_new_1 =   BugMergeTask(None, [bug3a], None, True)        #new bug
    
    #Test 
    task = sync.merge_bug(merge_task_known_2)
    print task   
     
    assert isinstance(task, BugWriteTask)
    assert isinstance(task.bug, BugIntl)
    assert "repo_a" in task.ids
    assert "repo_b" in task.ids
    bug = task.bug
    assert bug.time_modified == datetime(2000, 3, 2)
    assert bug.time_created == datetime(2000, 1, 1)
    assert bug.text_long == 'Description of bug one.\nAddition from repo_b\n'
    assert bug.status == "in_progress"
    assert bug.priority == "major"
    
    #Test 
    task = sync.merge_bug(merge_task_known_1)
    print task
    
    assert "repo_a" in task.ids
    assert "repo_b" in task.ids
    bug = task.bug
    assert bug.time_modified == datetime(2000, 3, 1)
    assert bug.time_created == datetime(2000, 1, 1)
    assert bug.text_long == 'Description of bug one.\nAddition from repo_a\n'
    assert bug.status == "confirmed"
    assert bug.priority == "major"

    #Test 
    task = sync.merge_bug(merge_task_new_2)
    print task    
    
    assert "repo_a" in task.ids
    assert "repo_b" in task.ids
    bug = task.bug
    assert bug.time_modified == datetime(2000, 3, 2)
    assert bug.time_created == datetime(2000, 1, 1)
    assert bug.text_long == 'Description of bug 3 from repo_a\nDescription of bug 3 from repo_b'
    assert bug.status == "in_progress"
    assert bug.priority == "major"
    
    
    task = sync.merge_bug(merge_task_new_1)
    print task
    assert "repo_a" in task.ids
    assert "repo_b" not in task.ids
    bug = task.bug
    assert bug.time_modified == datetime(2000, 3, 1)
    assert bug.time_created == datetime(2000, 1, 1)
    assert bug.text_long == 'Description of bug 3 from repo_a'
    assert bug.status == "confirmed"
    assert bug.priority == "major"
        


def test_RepoSyncer__merge_bugs__text():
    """
    Merging different versions of a bug. Test the text merging aspect 
    with three repositories.
    """
    #The example texts:
    text0 = textwrap.dedent(
        """
        Common line 1
        Only in text 0
        Common line 2
        Common line 3
        Common line 4
        Common line 5
        Different in all files, V 0
        Common line 6
        Different in text 0
        Common line 7
        Same in text 0, 2, 3
        Common line 8
        Same in text 0, 1, 3
        Common line 9
        Same in text 0, 1, 2
        Common line 10
        Common line 11
        Exists in text 0, 2, 3, but not in 1
        Common line 12
        Exists in text 0, 1, 3, but not in 2
        Common line 13
        Exists in text 0, 1, 2, but not in 3
        Common line 14
        """)
    text1 = textwrap.dedent(
        """
        Common line 1
        Common line 2
        Only in text 1
        Common line 3
        Common line 4
        Common line 5
        Different in all files, V 1
        Common line 6
        Same in text 1, 2, 3
        Common line 7
        Different in text 1
        Common line 8
        Same in text 0, 1, 3
        Common line 9
        Same in text 0, 1, 2
        Common line 10
        Exists in text 1, 2, 3, but not in 0
        Common line 11
        Common line 12
        Exists in text 0, 1, 3, but not in 2
        Common line 13
        Exists in text 0, 1, 2, but not in 3
        Common line 14
        """)
    text2 = textwrap.dedent(
        """
        Common line 1
        Common line 2
        Common line 3
        Only in text 2
        Common line 4
        Common line 5
        Different in all files, V 2
        Common line 6
        Same in text 1, 2, 3
        Common line 7
        Same in text 0, 2, 3
        Common line 8
        Different in text 2
        Common line 9
        Same in text 0, 1, 2
        Common line 10
        Exists in text 1, 2, 3, but not in 0
        Common line 11
        Exists in text 0, 2, 3, but not in 1
        Common line 12
        Common line 13
        Exists in text 0, 1, 2, but not in 3
        Common line 14
        """)
    text3 = textwrap.dedent(
        """
        Common line 1
        Common line 2
        Common line 3
        Common line 4
        Only in text 3
        Common line 5
        Different in all files, V 3
        Common line 6
        Same in text 1, 2, 3
        Common line 7
        Same in text 0, 2, 3
        Common line 8
        Same in text 0, 1, 3
        Common line 9
        Different in text 3
        Common line 10
        Exists in text 1, 2, 3, but not in 0
        Common line 11
        Exists in text 0, 2, 3, but not in 1
        Common line 12
        Exists in text 0, 1, 3, but not in 2
        Common line 13
        Common line 14
        """)
    #Create the bugs that contain the texts:
    bug, _ = make_bugs()
    bug0 = bug._replace(repo_name="INTERNAL", id="0", 
                        time_modified=datetime(2000, 2, 1), text_long=text0)
    bug1 = bug._replace(repo_name="repo_a", id="0", 
                        time_modified=datetime(2000, 2, 2), text_long=text1)
    bug2 = bug._replace(repo_name="repo_b", id="0", 
                        time_modified=datetime(2000, 2, 3), text_long=text2)
    bug3 = bug._replace(repo_name="repo_c", id="0", 
                        time_modified=datetime(2000, 2, 4), text_long=text3)
    
    #Create synchronization object with three repositories.
    repos = [DummyRepoData(repo_name="repo_a", initial_bugs=[]), 
             DummyRepoData(repo_name="repo_b", initial_bugs=[]), 
             DummyRepoData(repo_name="repo_c", initial_bugs=[])]
    task_data = make_dummy_task()._replace(repos_list=repos)  
    sync = RepoSyncer(task_data, 
                            [KnownBugData(ids={"INTERNAL":"0", "repo_a":"0", 
                                               "repo_b":"0", "repo_c":"0"},
                                          bug=bug0)])
    
    #Tasks to merge the contents of certain bugs
    #Bug0 is the internal bug, the other bugs are changed versions of the bug 
    #from the repositories. bug3 is the youngest bug.
    mt = BugMergeTask(bug0, [bug1, bug2, bug3], bug0.id, False) 
    
    #merge the bugs
    wt = sync.merge_bug(mt)
    
    #Test the merged text
#    print wt
    print wt.bug.text_long
    lines = wt.bug.text_long.split("\n")
    #Text must contain all common lines
    comlines = [l for l in lines if l.startswith("Common")] 
    assert len(comlines) == 14
    #Deletions from the internal version must not appear in the merged text
    assert "Only in text 0" not in lines
    #additions from changed versions must appear in the merged text 
    #(if non conflicting)
    newlines = [l for l in lines if l.startswith("Only")]
    assert len(newlines) == 3
    #Non conflicting changes from new versions must appear in text
    assert "Same in text 1, 2, 3" in lines
    #Changes from each version must appear in the text
    difflines = [l for l in lines if l.startswith("Different in text")]
    assert len(difflines) == 3
    #In lines that conflict in all four versions the youngest version is taken
    assert "Different in all files, V 3" in lines
    
    print "finished successfully."



def test_RepoSyncer__write_bugs_2():
    """
    Test uploading bug to the repositories.
    Somewhat unrealistic base scenario.
    
    #TODO: more test cases!
    """
    #Create three bugs
    bug0, _ = make_bugs()
    
    #Create synchronization object with two repositories
    task_data = make_dummy_task()
    sync = RepoSyncer(task_data, [])
    repo_a, repo_b = sync.repo_controllers
#    pipe_a, pipe_b = sync.bug_pipelines
    
    #Fill repositories and synchronization object with bugs:
    #Repository "repo_a"  and "repo_b" contain the bug
    #(However the bug pipeline does not know about the bugs; unrealistic.)
    id0a, = repo_a.create_bugs([bug0])
    id0b, = repo_b.create_bugs([bug0])
    repo_a.num_created, repo_b.num_created = 0, 0
    repo_a.num_updated, repo_b.num_updated = 0, 0    
#    #Let pipelines cache the bug.
#    pipe_a.get_recent_changes(datetime(1970, 1, 1))
#    pipe_b.get_recent_changes(datetime(1970, 1, 1))
    #Sync object: make bug0 known, and force ID "000000";  
    id0i = sync.known_bug_create(bug0, {"repo_a":id0a, "repo_b":id0b,}, "000000")
    
    #The task for uploading:
    #bug0: update in both repositories
    tasks = [BugWriteTask(ids={"INTERNAL":id0i, "repo_a":id0a, "repo_b":id0b},
                          bug=bug0,
                          internal_id=id0i,
                          create_intl=False),
             ]
    
    #the test
    sync.write_bugs(tasks)
    
    assert repo_a.num_created == 0
    assert repo_b.num_created == 0
    
    assert repo_a.num_updated == 1
    assert repo_b.num_updated == 1



#def test_RepoSyncer__write_bugs__create():
#    """
#    Test uploading bug to the repositories.
#    
#    Create in one repository, no update in the other.
#    The scenario is a newly discovered bug in "repo_a".
#    """
#    pytest.skip("RepoSyncer.write_bugs does currently not create bugs at all.")
#    #Create three bugs
#    bug0, _ = make_bugs()
#    
#    #Create synchronization object with two repositories
#    task_data = make_dummy_task()
#    sync = RepoSyncer(task_data, [])
#    repo_a, repo_b = sync.repo_controllers
#    pipe_a, pipe_b = sync.bug_pipelines
#    
#    #Fill repositories and synchronization object with bugs:
#    #Repository "repo_a" contains the bug
#    id0a, = repo_a.create_bugs([bug0])
#    repo_a.num_created, repo_b.num_created = 0, 0
#    #Let pipelines cache the bug. (really only ``pipe_a``)
#    pipe_a.get_recent_changes(datetime(1970, 1, 1))
#    pipe_b.get_recent_changes(datetime(1970, 1, 1))
#    #Sync object: bug0, is unknown;  
##    id0i = sync.known_bug_create(bug0, {"repo_a":id0a, "repo_b":id0b,}, "000000")
#    
#    #The task for uploading:
#    tasks = [BugWriteTask(ids={"repo_a":id0a}, 
#                          bug=bug0,
#                          internal_id=None,
#                          create_intl=True)]
#    
#    #the test
#    sync.write_bugs(tasks)
#    
#    assert repo_a.num_created == 0
#    assert repo_b.num_created == 1
#    
#    assert repo_a.num_updated == 0
#    assert repo_b.num_updated == 0



def test_RepoSyncer__synchronize_repos_1a():
    """
    Synchronize two dummy (in memory) repositories
    Test that the bugs are really synchronized.
    
    A single bug is created in one repository, ``repo_a``, and it is later 
    changed. The synchronization mechanism must create the bug in 
    ``repo_b``, and it must later update the bug to its new state.
    """
    #Create synchronization object with two dummy repositories.
    task_data = make_dummy_task()    
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #put a single bug into repository ``repo_a``
    t0 = datetime.utcnow()
    buga0, _ = make_bugs()
    ida, = repo_a.create_bugs([buga0])
    #synchronize the repositories
    sync.synchronize_repos(t0)
    
    repo_a.print_repo()
    repo_b.print_repo()
    #repos must contain same number of bugs after synchronization
    assert len(repo_a.bugs) == len(repo_b.bugs) == 1
    #get bug from each repository and test that it is in fact the same bug.
    buga1, = repo_a.get_bugs([ida])
    bugb1, = repo_b.get_recent_changes(datetime(1970, 1, 1))
    assert equal_contents(buga1, bugb1) and equal_contents(buga1, buga0) 
    #Only one bug created in each repository
    assert repo_a.num_created == 1
    assert repo_a.num_updated == 0
    assert repo_b.num_created == 1
    assert repo_b.num_updated == 0
    
    #Change the bug in repository ``repo_a``
    sleep(0.1)
    t1 = datetime.utcnow()
    buga2 = buga1._replace(text_long="New text for bug.")
    repo_a.update_bugs([buga2], [ida])
    #synchronize the repositories
    sync.synchronize_repos(t1)
    
    repo_a.print_repo()
    repo_b.print_repo()
    #repos must contain same number of bugs after synchronization
    assert len(repo_a.bugs) == len(repo_b.bugs) == 1
    #get bug from each repository and test that it has the same contents.
    buga3, = repo_a.get_bugs([ida])
    bugb3, = repo_b.get_recent_changes(datetime(1970, 1, 1))
    assert equal_contents(buga3, bugb3) 
    #The synchronization should have only updated the bug in ``repo_b``;
    #the update in ``repo_a`` was done manually above.
    assert repo_a.num_created == 1
    assert repo_a.num_updated == 1
    assert repo_b.num_created == 1
    assert repo_b.num_updated == 1



def test_RepoSyncer__synchronize_repos_1b():
    """
    Synchronize two dummy (in memory) repositories
    Test that there are no unnecessary bug updates and creations.
    
    Create two bugs in repository ``repo_a``, and later change them. The 
    synchronization algorithm must replicate these actions in ``repo_b``.
    The test only counts the numbers of bug creations and updates in each 
    repository.
    """
    #Create synchronization object with two dummy repositories.
    task_data = make_dummy_task()    
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #put some bugs into repository ``repo_a``
    t0 = datetime.utcnow()
    bugs = make_bugs()
    id0, id1 = repo_a.create_bugs(bugs)
    #synchronize the repositories
    sync.synchronize_repos(t0)
    
    repo_a.print_repo()
    repo_b.print_repo()
    #repos must contain same number of bugs
    assert len(repo_a.bugs) == len(repo_b.bugs) == len(bugs)
    assert repo_a.num_created == len(bugs)
    assert repo_a.num_updated == 0
    assert repo_b.num_created == len(bugs)
    assert repo_b.num_updated == 0
    
    #Change some bugs in repository ``repo_a`` later
    sleep(0.1)
    t1 = datetime.utcnow()
    bug0g, bug1g = repo_a.get_bugs([id0, id1])
    bug0m = bug0g._replace(text_long="New text for bug 0")
    bug1m = bug1g._replace(text_long="New text for bug 1")
    repo_a.update_bugs([bug0m, bug1m], [id0, id1])
    #synchronize the repositories
    sync.synchronize_repos(t1)
    
    repo_a.print_repo()
    repo_b.print_repo()
    #repos must contain same number of bugs
    assert len(repo_a.bugs) == len(repo_b.bugs) == len(bugs)
    assert repo_a.num_created == len(bugs)
    assert repo_a.num_updated == 2
    assert repo_b.num_created ==  len(bugs)
    assert repo_b.num_updated == 2



def test_RepoSyncer__synchronize_repos_2():
    """
    Synchronize two dummy (in memory) repositories
    Test that new bugs with the same title, are really recognized as 
    two versions of the same bug.
    
    A two bugs are created in each repository. Each bug has a corresponding
    bug in the other repository with the same contents. The synchronization 
    algorithm must recognize these bugs as two versions of the same bug.
    It must put the bugs into its internal storage, but must not 
    modify the repositories.
    """
    #Create synchronization object with two dummy repositories.
    task_data = make_dummy_task()    
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #put a single bug into both repositories
    bug0, bug1 = make_bugs()
    id0_a, id1_a = repo_a.create_bugs([bug0, bug1])
    id0_b, id1_b = repo_b.create_bugs([bug0, bug1])
    #synchronize the repositories
    sync.synchronize_repos(datetime(1970, 1, 1))
    
    repo_a.print_repo()
    repo_b.print_repo()
    #repos must contain same number of bugs after synchronization
    assert len(repo_a.bugs) == len(repo_b.bugs) == 2
    #get bug0 from each repository and test that it is in fact the same bug.
    bug0a, = repo_a.get_bugs([id0_a])
    bug0b, = repo_b.get_bugs([id0_b])
    assert equal_contents(bug0a, bug0b) and equal_contents(bug0a, bug0) 
    #get bug1 from each repository and test that it is in fact the same bug.
    bug1a, = repo_a.get_bugs([id1_a])
    bug1b, = repo_b.get_bugs([id1_b])
    assert equal_contents(bug1a, bug1b) and equal_contents(bug1a, bug1) 
    #Only 2 bugs created in each repository, no updates
    assert repo_a.num_created == 2
    assert repo_a.num_updated == 0
    assert repo_b.num_created == 2
    assert repo_b.num_updated == 0
    
    #Look into the internal storage
    assert len(sync.known_bugs) == 2
    bug0r, _ = sync.known_bug_find("repo_a", "a0")
    bug1r, _ = sync.known_bug_find("repo_a", "a1")
    assert equal_contents(bug0r, bug0)
    assert equal_contents(bug1r, bug1)
    


def test_RepoSyncer__synchronize_repos_3():
    """
    Synchronize two dummy (in memory) repositories
    Test 2-way and 3-way merging
    
    A a bug is created in each repository, with the same title. The 
    synchronization algorithm must recognize these bugs as two versions of 
    the same bug. 
    Then both bugs are modified, the algorithm must modify both bugs.
    """
    #Create synchronization object with two dummy repositories.
    task_data = make_dummy_task()    
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #Create two test bugs, same title different description
    bug_, _ = make_bugs()
    buga = bug_._replace(text_long=u"Version a.")
    bugb = bug_._replace(text_long=u"Version b.")
    all_lines = set([buga.text_long, bugb.text_long])
    
    #put a single bug into each repository
    t0 = datetime.utcnow()
    ida, = repo_a.create_bugs([buga])
    idb, = repo_b.create_bugs([bugb])
    #synchronize the repositories
    sync.synchronize_repos(t0)
    
    repo_a.print_repo()
    repo_b.print_repo()
    #repos must contain same number of bugs after synchronization
    assert len(repo_a.bugs) == len(repo_b.bugs) == 1
    #see if text was merged - all texts must contain all lines
    buga1, = repo_a.get_bugs([ida])
    bugb1, = repo_b.get_bugs([idb])
    assert all_lines == set(buga1.text_long.split("\n")) \
                     == set(bugb1.text_long.split("\n"))
           
    #Later modify both bugs
    sleep(0.1)
    t1 = datetime.utcnow()
    buga2 = buga1._replace(text_long=u"Start a\nVersion a.\nVersion b.")
    bugb2 = bugb1._replace(text_long=u"Version a.\nVersion b\nEnd b.")
    repo_a.update_bugs([buga2], [ida])
    repo_b.update_bugs([bugb2], [idb])
    #synchronize
    sync.synchronize_repos(t1)
    
    repo_a.print_repo()
    repo_b.print_repo()
    #See if text was really merged
    buga3, = repo_a.get_bugs([ida])
    bugb3, = repo_b.get_bugs([idb])
    assert buga3.text_long == bugb3.text_long 
    #TODO: more comprehensive test
    
    
    
def test_RepoSyncer__synchronize_repos__dry_run():
    """
    Test parameter ``dry_run`` of ``RepoSyncer.synchronize_repos``
    This parameter prevents the synchronization algorithm from changing the 
    repositories.
    
    Create two bugs in repository ``repo_a``. Synchronize with ``dry_run=True``.
    The  synchronization algorithm must not change the repositories, nor must 
    advance the last sync time.
    """
    #Create synchronization object with two dummy repositories.
    task_data = make_dummy_task()    
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #put some bugs into repository ``repo_a``
    t0 = datetime.utcnow()
    bugs = make_bugs()
    repo_a.create_bugs(bugs)
    #synchronize the repositories
    next_sync_time, _ = sync.synchronize_repos(t0, dry_run=True)
    
    repo_a.print_repo()
    repo_b.print_repo()
    #repos must be unchanged by the synchronization function.
    assert len(repo_a.bugs) == 2 == len(bugs)
    assert len(repo_b.bugs) == 0
    assert repo_a.num_created == 2 
    assert repo_a.num_updated == 0
    assert repo_a.num_read == 2
    assert repo_b.num_created == 0
    assert repo_b.num_updated == 0
    assert repo_b.num_read == 0
    #The sync time must also be unchanged
    assert next_sync_time == t0


def test_RepoSyncer__synchronize_repos__translate_buglinks_0():
    """
    Test the translation of links between bugs.
    
    Two synchronized repositories. A known bug is modified and it contains
    bug-links. The bug-links must be correctly translated when the changes are
    synchronized.
    
    This is "Simple Scenario" from:
    https://sourceforge.net/apps/trac/bug-repo-syncer/wiki/TranslateBugLinks
    """
    #create bugs
    #Repo A:
    bug0, bug1 = make_bugs()
    print bug0
    print bug1
    #Repo B:
    bug0b = bug0._replace(repo_name="repo_b", id="b0")
    bug1b = bug1._replace(repo_name="repo_b", id="b1")
    print bug0b
    print bug1b
    
    #Create synchronization object with two dummy repositories.
    #"repo_a" and "repo_b" each contain two synchronized bugs
    task_data = make_dummy_task()
    task_data = task_data._replace(
        repos_list=
            [DummyRepoData(repo_name="repo_a", initial_bugs=[bug0, bug1]), 
             DummyRepoData(repo_name="repo_b", initial_bugs=[bug0b, bug1b])])
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #synchronize the repositories to create known bug database
    sync.synchronize_repos(datetime(1970, 1, 1))
    print "create known bug database ------------------------------------------"
    repo_a.print_repo()
    repo_b.print_repo()
    pprint(sync.known_bugs)
    
    #Modify bug in "repo_a" to contain a bug-link.
    bug0am = bug0._replace(text_long="Link to bug #a1 in here.")
    repo_a.update_bugs([bug0am], ["a0"])
        
    #Synchronize the repositories and translate the bug-link.
    sync.synchronize_repos(datetime(1970, 1, 1))
    print "Synchronize and translate link -------------------------------------"
    repo_a.print_repo()
    repo_b.print_repo()
    pprint(sync.known_bugs)
 
    #Test "repo_b", where the algorithm must create the translated link -------
    #Get the bug
    mbug0b, = repo_b.get_bugs(["b0"])
    #The link must be translated, no discovery link
    assert mbug0b.text_long.find("bug #b1") != -1
    assert mbug0b.text_long.find("bug #a1") == -1
    assert mbug0b.text_long.find("BUGLINK") == -1
    #no extra lines in the text
    assert len(mbug0b.text_long.splitlines()) == 1

    #Test "repo_a", where the link was inserted manually --------------
    #The program must not mess it up
    #Get the bug
    mbug0a, = repo_a.get_bugs(["a0"])
    #We want the original link, no discovery link
    assert mbug0a.text_long.find("bug #a1") != -1
    assert mbug0a.text_long.find("bug #b1") == -1
    assert mbug0a.text_long.find("BUGLINK") == -1
    #no extra lines in the text
    assert len(mbug0a.text_long.splitlines()) == 1
    
    #Verify that the internal bug contains the correct link too.
    #Create the link text for "INTERNAL" 
    id_i = sync.id_trans.repo2intl("repo_a", "a1")
    link_text_i = "bug #{}".format(id_i)
    print "link_text_i:", link_text_i
    bug0i, _ = sync.known_bug_find("repo_a", "a0")
    assert bug0i.text_long.find(link_text_i) != -1



def test_RepoSyncer__synchronize_repos__translate_buglinks_1():
    """
    Test the translation of links between bugs.
    
    Unknown bugs with links are in one repository. The other repository is 
    empty. Bugs with consistent links between them must be created in the 
    other repository. No garbage text must be produced.
    
    This is "Complex Scenario 1" from:
    https://sourceforge.net/apps/trac/bug-repo-syncer/wiki/TranslateBugLinks
    """
    
    #create bugs with links in them
    bug0, bug1 = make_bugs()
    bug0a = bug0._replace(text_long="Link to bug #a0 is here.")
    bug1a = bug1._replace(text_long="Link to bug #a0 is here.")
    print bug0a
    print bug1a
    
    #Create synchronization object with two dummy repositories.
    #"repo_a" contains the two bugs
    task_data = make_dummy_task()
    task_data = task_data._replace(
        repos_list=[
            DummyRepoData(repo_name="repo_a", initial_bugs=[bug0a, bug1a]), 
            DummyRepoData(repo_name="repo_b", initial_bugs=[])])
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #synchronize the repositories
    #1. write bugs with discovery links
    sync.synchronize_repos(datetime(1970, 1, 1))
    print "pass 1 ------------------------------------------"
    repo_a.print_repo()
    repo_b.print_repo()
    pprint(sync.known_bugs)
    #2. read bugs with discovery links, translate them into regular links,
    #   write regular links
    sync.synchronize_repos(datetime(1970, 1, 1))
    print "pass 2 ------------------------------------------"
    repo_a.print_repo()
    repo_b.print_repo()
    pprint(sync.known_bugs)
    
    #Text of bug links in repository "repo_a" (for convenience)
    link_text_a = "bug #a0"
    #Create the link text for "INTERNAL" and for repository "repo_b"
    id_i = sync.id_trans.repo2intl("repo_a", "a0")
    link_text_i = "bug #{}".format(id_i)
    print "link_text_i:", link_text_i
    id_b = sync.id_trans.intl2repo("repo_b", id_i)
    link_text_b = "bug #{}".format(id_b)
    print "link_text_b:", link_text_b
    
    #Test "repo_b", where new bugs were created --------------
    #Get all bugs of "repo_b"
    mbug0b, mbug1b = repo_b.get_recent_changes(datetime(1970, 1, 1))
    #All links must be translated
    assert mbug0b.text_long.find(link_text_b) != -1
    assert mbug1b.text_long.find(link_text_b) != -1
    assert mbug0b.text_long.find(link_text_a) == -1
    assert mbug1b.text_long.find(link_text_a) == -1
    #No discovery links
    assert mbug0b.text_long.find("BUGLINK") == -1
    assert mbug1b.text_long.find("BUGLINK") == -1
    
    #no extra lines in the text
    assert len(mbug0b.text_long.splitlines()) == 1
    assert len(mbug1b.text_long.splitlines()) == 1
    
    #Test "repo_a", where the bugs originally came from --------------
    #No bugs must have been changed on this repository
    assert repo_a.num_created == 0
    assert repo_a.num_updated == 0
    
    #Verify that the known bugs contain the correct links too.
    kbd0, kbd1 = sync.known_bugs.values()
    text_k0 = kbd0.bug.text_long
    text_k1 = kbd1.bug.text_long
    assert text_k0.find(link_text_i) != -1
    assert text_k1.find(link_text_i) != -1
    
    

def test_RepoSyncer__synchronize_repos__translate_buglinks_2():
    """
    Test the translation of links between bugs.
    
    Two synchronized repositories where bugs have links between them, 
    but all bugs are unknown. (The database of known bugs has been lost).
    The algorithm must create the database of known bugs without special 
    intervention by the user. It must not create any garbage text.
    
    This is "Complex Scenario 2" from:
    https://sourceforge.net/apps/trac/bug-repo-syncer/wiki/TranslateBugLinks
    """
    #create bugs with links in them
    #Repo A:
    bug0, bug1 = make_bugs()
    bug0a = bug0._replace(text_long="Link to bug #a0 is here.")
    bug1a = bug1._replace(text_long="Link to bug #a0 is here.")
    print bug0a
    print bug1a
    #Repo B:
    mbug0b = bug0._replace(repo_name="repo_b", id="b0", 
                           text_long="Link to bug #b0 is here.")
    mbug1b = bug1._replace(repo_name="repo_b", id="b1", 
                           text_long="Link to bug #b0 is here.")
    print mbug0b
    print mbug1b
    
    #Create synchronization object with two dummy repositories.
    #"repo_a" contains the two bugs
    task_data = make_dummy_task()
    task_data = task_data._replace(
        repos_list=
            [DummyRepoData(repo_name="repo_a", initial_bugs=[bug0a, bug1a]), 
             DummyRepoData(repo_name="repo_b", initial_bugs=[mbug0b, mbug1b])])
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #synchronize the repositories
    #1. write bugs with discovery links
    sync.synchronize_repos(datetime(1970, 1, 1))
    print "pass 1 ------------------------------------------"
    repo_a.print_repo()
    repo_b.print_repo()
    pprint(sync.known_bugs)
    #2. read bugs with discovery links, translate them into regular links,
    #   write regular links
    sync.synchronize_repos(datetime(1970, 1, 1))
    print "pass 2 ------------------------------------------"
    repo_a.print_repo()
    repo_b.print_repo()
    pprint(sync.known_bugs)
 
    #No bugs must have been changed in any repository
    assert repo_a.num_created == 0
    assert repo_a.num_updated == 0
    assert repo_b.num_created == 0
    assert repo_b.num_updated == 0
    
    #Create the link text for "INTERNAL" 
    id_i = sync.id_trans.repo2intl("repo_a", "a0")
    link_text_i = "bug #{}".format(id_i)
    print "link_text_i:", link_text_i
    #Verify that the known bugs contain the right links.
    kbd0, kbd1 = sync.known_bugs.values()
    text_k0 = kbd0.bug.text_long
    text_k1 = kbd1.bug.text_long
    assert text_k0.find(link_text_i) != -1
    assert text_k1.find(link_text_i) != -1
    
 
 
def test_RepoSyncer__synchronize_repos__translate_buglinks_configuration():
    """
    Test if translation of links between bugs can be switched off.
    
    Translating bug-links is switched off.
    Unknown bugs with links are in one repository. The other repository is 
    empty. The program must not change the text.
    """
    
    #create bugs with links in them
    bug0, _ = make_bugs()
    bug0a = bug0._replace(text_long="Link to bug #a0 is here.")
    print bug0a
    
    #Create synchronization object with two dummy repositories.
    #"repo_a" contains the two bugs
    task_data = make_dummy_task()
    task_data = task_data._replace(
        repos_list=[
            DummyRepoData(repo_name="repo_a", initial_bugs=[bug0a]), 
            DummyRepoData(repo_name="repo_b", initial_bugs=[])],
        translate_bug_links=False)
    sync = RepoSyncer(task_data)
    #get the repositories
    repo_a, repo_b = sync.repo_controllers
    
    #synchronize the repositories
    sync.synchronize_repos(datetime(1970, 1, 1))
    print "pass 1 ------------------------------------------"
    repo_a.print_repo()
    repo_b.print_repo()
    pprint(sync.known_bugs)
    
    #Test "repo_b", where new bugs were created --------------
    #Get all bugs of "repo_b"
    mbug0b, = repo_b.get_recent_changes(datetime(1970, 1, 1))
    #The text must be preserved exactly
    assert mbug0b.text_long == "Link to bug #a0 is here."
    
    #Test "repo_a", where the bugs originally came from --------------
    #No bugs must have been changed on this repository
    assert repo_a.num_created == 0
    assert repo_a.num_updated == 0
    
    #Verify that the known bugs contain text unchanged too.
    kbd0, = sync.known_bugs.values()
    assert kbd0.bug.text_long == "Link to bug #a0 is here."
    
    

def debug_RepoSyncer__synchronize_repos():
    """
    Call this function to debug the synchronization algorithm with the 
    real repositories. Logs in anonymously.
    """
    #Create synchronization object with two dummy repositories.
    task_data = example_conf.repo_config
    sync = RepoSyncer(task_data)
    #get the repositories
    ctrl_lp, ctrl_trac = sync.repo_controllers
    
    sync.synchronize_repos(datetime(1970, 1, 1))
    


def perf_bug_comparison_funcs():
    """
    Test the speed of bug comparison algorithms
    
    Result:
        `equal_contents` is slightly faster. 
        * Ratio ~ 0.7  for same number of equal and unequal bugs.
        * Ratio ~ 0.3  (much faster) for only unequal bugs.
        * Ratio ~ 0.95 for only equal bugs.
    """
    
    BUG_CONTENTS_FIELDS = list(set(BugIntl._fields).difference(
                                        ["ids", "time_created", "time_modified"]))
    def equal_contents(bug1, bug2): #IGNORE:W0621
        """ 
        Test if bugs are equal, but ignore fields that the repositories 
        always change. (ids, time_created, time_modified)
        """
        for fname in BUG_CONTENTS_FIELDS:
            if getattr(bug1, fname) != getattr(bug2, fname):
                return False
        return True
    
    def make_bugs_comparable(bug): #IGNORE:W0621
        """
        Set bugs to neutral state, so that it can be compared.
        """
        return bug._replace(ids={}, time_created=None, time_modified=None)

    
    bug0a, bug1 = make_bugs()
    bug0b, _    = make_bugs()
    
    n_test = 100000
    print "Doing {} iterations...".format(n_test)
    
    t0 = clock()
    for _ in xrange(n_test):
        assert not equal_contents(bug0a, bug1)
        assert equal_contents(bug0a, bug0b)
    t1 = clock()
    for _ in xrange(n_test):
        assert make_bugs_comparable(bug0a) != make_bugs_comparable(bug1)
        assert make_bugs_comparable(bug0a) == make_bugs_comparable(bug0b)
    t2 = clock()
    
    t_ec = t1 - t0
    t_mbc = t2 - t1
    print "`equal_contents`       : {} s,".format(t_ec)
    print "`make_bugs_comparable` : {} s.".format(t_mbc)
    print "ratio: {}".format(t_ec / t_mbc)
    


#---------------------- Test BugPipeline -------------------------------
#==========================================================================

class FilterSwapCase(FilterBase):
    """
    Swap the case of all characters in text_short and text_long. For test code.
    
    TODO: change into metal umlaut filter. Metal umlauts in the repository,
          no umlauts (no dots) internally. This gives the ability to have a 
          metal umlaut repository and a regular one (for English text). 
    """
    def __init__(self):
        FilterBase.__init__(self)
        
    def intl2repo(self, bug):
        """Translate: internal -> repository."""
        assert isinstance(bug, BugIntl)
        trbug = bug._replace(text_short=bug.text_short.swapcase(), 
                             text_long=bug.text_long.swapcase(), )
        return trbug
    
    def repo2intl(self, bug):
        """Translate: repository -> internal."""
        assert isinstance(bug, BugIntl)
        trbug = bug._replace(text_short=bug.text_short.swapcase(), 
                             text_long=bug.text_long.swapcase(), )
        return trbug

   

def test_BugPipeline__filter():
    "BugPipeline: Test the filtering functionality."
    frepo = FilterNoop()
    fcase = FilterSwapCase()
    bug0, _ = make_bugs()
    ctrl = RepoControllerDummy(DummyRepoData("repo_a", [bug0]))

    #create pipeline that swaps case in texts
    pipe = BugPipeline(ctrl, equal_contents, frepo, [fcase], [])
    
    #Call filter function directly
    b0f =  pipe.filter_intl2repo(bug0)
    assert b0f.text_long == bug0.text_long.swapcase()
    b0f =  pipe.filter_repo2intl(bug0)
    assert b0f.text_long == bug0.text_long.swapcase()

    #TODO: test where direction of filters, and their order is important.
    
    #Upload bug and see if it is filtered
    pipe.queue_update(bug0, "a0")
    pipe.upload_queued_bugs()
    b0u, = ctrl.get_bugs(["a0"])
    assert b0u.text_long == bug0.text_long.swapcase()
    
    #Retrieve bug - it must be in original state again
    b0r, = pipe.get_recent_changes(datetime(1970, 1, 1))
    assert b0r.text_long == bug0.text_long
    
    print "finished test_BugPipeline__filter"
    


def test_BugPipeline__queue_update():
    "BugPipeline: Test method queue_update."
    frepo = FilterNoop()
    bug0, bug1 = make_bugs()
    ctrl = RepoControllerDummy(DummyRepoData("repo_a", [bug0]))
    
    #create pipeline that does no translations
    pipe = BugPipeline(ctrl, equal_contents, frepo, [], [bug0])

    #These tests really test implementation details -----------
    #Try to put bug in queue that is already in cache. It must be rejected.
    pipe.queue_update(bug0, "a0")
    assert len(pipe.up_bugs) == 0
    
    #Put modified version of bug in queue, it must get into queue.
    bug0m = bug0._replace(text_short="test")
    pipe.queue_update(bug0m, "a0")
    assert len(pipe.up_bugs) == 1
    
    #Put bug in queue that is not in cache
    pipe.queue_update(bug1, "a1")
    assert len(pipe.up_bugs) == 2
    
#    pprint(pipe.up_bugs)
#    pprint(pipe.dl_cache)
    
    #These tests test real functionality --------------
    #create pipeline that does no translations
    pipe = BugPipeline(ctrl, equal_contents, frepo, [], [])
    
    #Get bug0 from repository, and put it into cache
    pipe.get_recent_changes(datetime(1970, 1, 1))
    
    #Queue existing, unchanged bug, and upload it
    pipe.queue_update(bug0, "a0")
    pipe.upload_queued_bugs()
    #The queue must not upload the bug
    assert ctrl.num_updated == 0
    
    #Queue modified bug, and upload it
    bug0m = bug0._replace(text_short="test")
    pipe.queue_update(bug0m, "a0")
    pipe.upload_queued_bugs()
    #The queue must upload the bug
    assert ctrl.num_updated == 1
    
    print "finished test_BugPipeline__queue_update"
    


def test_BugPipeline__queue_create():
    "BugPipeline: Test method queue_update."
    frepo = FilterNoop()
    bug0, bug1 = make_bugs()
    ctrl = RepoControllerDummy(DummyRepoData("repo_a", [bug0]))
    
    #create pipeline that does no translations
    pipe = BugPipeline(ctrl, equal_contents, frepo, [], [bug0])

    #These tests really test implementation details -----------
    #Put bug in create queue 
    pipe.queue_create(bug1)
    assert len(pipe.cr_bugs) == 1

    pprint(pipe.cr_bugs)
#    pprint(pipe.up_bugs)
#    pprint(pipe.dl_cache)
    
    #These tests test real functionality --------------
    #create pipeline that does no translations
    pipe = BugPipeline(ctrl, equal_contents, frepo, [], [])
    
    #Put bug in create queue and upload it
    pipe.queue_create(bug1)
    pipe.upload_queued_bugs()
    #The bug must have been created in the repository
    assert ctrl.num_created == 1
    
    print "finished test_BugPipeline__queue_create"



def test_BugPipeline__get_recent_changes():
    "BugPipeline: Test method queue_update."
    frepo = FilterNoop()
    bug0, bug1 = make_bugs()
    ctrl = RepoControllerDummy(DummyRepoData("repo_a", [bug0, bug1]))
    
    #create pipeline that does no translations
    pipe = BugPipeline(ctrl, equal_contents, frepo, [], [])
    
    #get_recent_changes must get bugs from repository
    bugs = pipe.get_recent_changes(datetime(1970, 1, 1))
    assert len(bugs) == 2
    assert set(bugs) == set([bug0, bug1])
    
    #also the cache must be filled
    assert len(pipe.dl_cache) == 2



def test_BugPipeline__create_repo_objects():
    """
    Test factory function ``create_repo_objects``. 
    Test BugPipeline with the Trac repository. Get recent changes.
    """
    
    controller, comparator, converter = create_repo_objects(
                                                        example_conf.trac_data)
    
    pmf = PeopleMilestoneFilter("trac", example_conf.people, 
                                example_conf.milestones)
    
    pipe = BugPipeline(controller, comparator, converter, [pmf])
    bugs = pipe.get_recent_changes(datetime(2012, 1, 1))
    
    print len(bugs), type(bugs[0])
    assert len(bugs) > 10
    assert all([isinstance(bug, BugIntl) for bug in bugs])



if __name__ == '__main__':
    #The tests use those objects to see if they should be skipped or executed
    #The test runner ``py.test`` creates these objects normally.
    #pylint: disable=W0201
    class Dummy(object): pass
    pytest.config = Dummy()
    pytest.config.option = Dummy()
    pytest.config.option.slow_and_dangerous = True
    pytest.config.option.modify_launchpad = True
    pytest.config.option.modify_trac = True
    pytest.config.option.trac_password = None
    
#    test_start_script()
    
#    test_ApplicationMain__parse_args()
#    test_ApplicationMain__main__version_help()
#    test_ApplicationMain__main__info()
#    test_ApplicationMain__main__init()
#    test_ApplicationMain__main__sync_errors()
#    test_ApplicationMain__read_data()
    
#    test_RepoSyncer__creation()
#    test_RepoSyncer__create_id_translator()
#    test_RepoSyncer__discover_milestones()
#    test_RepoSyncer__create_new_id()
#    test_RepoSyncer__add_known_bug()
#    test_RepoSyncer__known_bug_update()
#    test_RepoSyncer__known_bug_find()
#    test_RepoSyncer__get_recent_changes()
#    test_RepoSyncer__find_associated_bugs()
#    test_RepoSyncer_create_preliminary_bugs()
#    test_RepoSyncer_translate_bug_links()
#    test_RepoSyncer__merge_diff3()
#    test_RepoSyncer__merge_2way()
#    test_RepoSyncer__merge_bugs()
#    test_RepoSyncer__merge_bugs__text()
#    test_RepoSyncer__write_bugs_2()
#    test_RepoSyncer__write_bugs__create()
#    test_RepoSyncer__synchronize_repos_1a()
#    test_RepoSyncer__synchronize_repos_1b()
#    test_RepoSyncer__synchronize_repos_2()
#    test_RepoSyncer__synchronize_repos_3()
#    test_RepoSyncer__synchronize_repos__dry_run()
#    test_RepoSyncer__synchronize_repos__translate_buglinks_0()
#    test_RepoSyncer__synchronize_repos__translate_buglinks_1()
#    test_RepoSyncer__synchronize_repos__translate_buglinks_2()
#    test_RepoSyncer__synchronize_repos__translate_buglinks_configuration()
#    perf_bug_comparison_funcs()

#    test_BugPipeline__filter()
#    test_BugPipeline__queue_update()
#    test_BugPipeline__queue_create()
#    test_BugPipeline__get_recent_changes()
    test_BugPipeline__create_repo_objects()
