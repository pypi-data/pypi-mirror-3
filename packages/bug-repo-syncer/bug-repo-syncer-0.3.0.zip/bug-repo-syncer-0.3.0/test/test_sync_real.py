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
Test synchronization with the real repositories.
"""

from __future__ import division
from __future__ import absolute_import              

import pytest #contains `skip`, `fail`, `raises`, `config`

import os
import sys
import stat
import shutil
import textwrap
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from time import sleep 
from pprint import pprint

from test.helpers import delete_bugs_safe_trac, repair_test_bugs_lp, \
    repair_test_bugs_trac
import bug_repo_syncer.example_conf as example_conf
from bug_repo_syncer.common import BugIntl, equal_contents
from bug_repo_syncer.repo_io import TracController, BugTrac, \
    LpController, BugLp
from bug_repo_syncer.main import ApplicationMain



def make_bugs():
    """Create bugs, that match the dummy task"""
    bug_in = BugIntl(repo_name=None, id=None,                   #administrative
                     time_created=datetime(2000, 1, 1), 
                     time_modified=datetime(2000, 2, 1), 
                     text_short=u"Test Bug Zero",               #text
                     text_long=u"Description of bug zero.", 
                     reporter="Eike Welk",                      #people
                     assigned_to="Eike Welk", 
                     status="in_progress", priority="minor",    #bug life cycle
                     resolution="none", kind="defect",
                     milestone="0.0.1")                         #grouping
    
    bug_tr = BugTrac(repo_name=None, id=None,                   #administrative
                     time_created=datetime(2000, 1, 1), 
                     time_modified=datetime(2000, 2, 1), 
                     summary=u"Test Bug Zero",                  #text
                     description=u"Description of bug zero.",  
                     reporter="eike",                           #people
                     owner="eike", 
                     status="accepted", priority="minor",       #bug life cycle
                     resolution="none", type="defect",
                     milestone="0.0.1")                         #grouping
    
    bug_lp = BugLp(repo_name=None, id=None,                     #administrative
                   time_created=datetime(2000, 1, 1), 
                   time_modified=datetime(2000, 2, 1), 
                   title=u"Test Bug Zero",                      #text
                   description=u"Description of bug zero.",  
                   owner="eike-welk",                           #people
                   assignee="eike-welk", 
                   status="In Progress",                        #bug life cycle
                   importance="Low", 
                   milestone="0.0.1")                           #grouping
    return bug_in, bug_tr, bug_lp



#Path to test root directory, relative to the location of this file
TEST_ROOT_REL_PATH = "tmp/sync"
#Name of setup directory. It contains configuration and data files that are 
#used by the tests.
SETUPDIR = "sync_real_setup"
    
def compute_path_names(testname):
    """
    Compute path names for the tests
    
    Returns
    ------- 
    test_root_dir
        absolute path of test root directory, ``proj_dir`` will be created there
    proj_dir
        absolute path of project directory, ``conf_file`` will be created there
    conf_file
        absolute path of configuration file for ``bsync`` program
    """
    test_root_dir = os.path.join(os.path.dirname(__file__), TEST_ROOT_REL_PATH)
    proj_dir = os.path.join(test_root_dir, testname)
    conf_file = os.path.join(proj_dir, "syncer_config.py")
    
    return test_root_dir, proj_dir, conf_file


def setup_test_resources(testname):
    """
    * Set up path names 
    * Delete old project directory
    * Create new project directory with configuration file and known bugs.
      Files are copied from ``SETUPDIR`` which is created by ``setup_module``
    
    Argument
    -------- 
    testname
        unique name of this test, becomes (part of) project directory's name
        
    Returns
    ------- 
    test_root_dir
        absolute path of test root directory, ``proj_dir`` will be created there
    proj_dir
        absolute path of project directory, ``conf_file`` will be created there
    conf_file
        absolute path of configuration file for ``bsync`` program
    """
    test_root_dir, proj_dir, conf_file = compute_path_names(testname)
    #create test root directory if none exists
    if not os.path.exists(test_root_dir):
        os.makedirs(test_root_dir)
    #create an empty project directory (hopefully uniquely named)
    if os.path.exists(proj_dir):
        print "Removing directory:", proj_dir
        os.chmod(proj_dir, stat.S_IRWXU)
        shutil.rmtree(proj_dir)
    os.mkdir(proj_dir)

    try:
        setup_dir = os.path.join(test_root_dir, SETUPDIR)
        #copy configuration file and known bugs that were created by the 
        #``setup_module`` function
        shutil.copy(os.path.join(setup_dir, "syncer_config.py"), 
                    os.path.join(proj_dir, "syncer_config.py"))
        shutil.copy(os.path.join(setup_dir, "sync-data.pickle"), 
                    os.path.join(proj_dir, "sync-data.pickle"))
    except IOError:
        #special handling for ``setup_module`` itself
        pass
    
    return test_root_dir, proj_dir, conf_file


def setup_module(_module):
    """
    ------------------------------------------------------------------
    This function is called by "py.test" at the start of the test run.
    ------------------------------------------------------------------
    
    * Set the test bugs to a defined state, and...
    
    * Synchronize the test repositories, so there is a (somewhat) consistent 
      starting point for the tests. 
      
    * Create configuration and data files that are used by the tests. 
      (The tests copy the configuration and data files to their individual test
      directories, with ``setup_test_resources("my_dir")``)
      
    * Data files, configuration files, and bugs on Trac are deleted and 
      created again every 7 days. (Not done more frequently as it 
      takes about 300 s.)
    
    All bugs are regularly deleted from the Trac repository, except for the 
    "sacred" test bugs. This way the bugs that are created by the test suite 
    can disappear from the test repositories when they are deleted from 
    Launchpad's test server. Otherwise tey would survive forever on Trac.
    """
    if not (pytest.config.option.slow_and_dangerous):
        pytest.skip("This is a time consuming test suite, " #IGNORE:E1101
                    "that modifies Trac and Launchpad")
    if pytest.config.option.dist != "no":
        pytest.skip("This test can not be run in parallel.") #IGNORE:E1101
    #Get password from test framework, stored in: ``conftest.py``
    passwords = {"trac":pytest.config.option.trac_password}
    
    #Setup some path names
    old_cwd = os.getcwd()
    _, proj_dir, _ = compute_path_names(SETUPDIR)
    timestamp = os.path.join(
                    os.path.dirname(__file__), TEST_ROOT_REL_PATH, "TIMESTAMP")
    try:
        age = datetime.utcnow() - \
              datetime.fromtimestamp(os.path.getmtime(timestamp))
    except (IOError, OSError):
        age = timedelta(days=1000) 
    print "Age of test root: ", age
    
    #Delete resources if they are too old. 
    if age > timedelta(days=7):
        #Delete all bugs on Trac
        tr_ctrl = TracController(example_conf.trac_data, authenticate=True,
                                 addpw=passwords)
        all_bugs = tr_ctrl.get_recent_changes(datetime(1970, 1, 1))
        delete_bugs_safe_trac(all_bugs, tr_ctrl)
        
        #create empty project directory, and go there
        _, proj_dir, _ = setup_test_resources(SETUPDIR)
        #Remember creation time of configuration and data files
        with open(timestamp, "w") as tsfile:
            tsfile.write(str(datetime.utcnow()))
        
        #Create configuration file for bsync
        os.chdir(proj_dir)
        assert call_application_main("bsync init") == "0"
        #Test if the configuration file works
        assert call_application_main("bsync info") == "0"
    
    #Set test bugs to a defined state
    repair_test_bugs_lp()
    repair_test_bugs_trac()
    #synchronize the test repositories
    os.chdir(proj_dir)
    assert call_application_main("bsync sync", passwords) == "0"
    
    os.chdir(old_cwd)
    

    
def call_application_main(arg_str, password_dict={}):  #IGNORE:W0102
    """
    Create application and call its main function. 
    ``arg_str`` contains the command line, as it would be typed into a shell.
    Return the program's return code.
    """
    app = ApplicationMain(password_dict)
    sys.argv = arg_str.split()
    try:
        app.main()
    except SystemExit, e:
        return str(e)
    else:
        assert False, "Must raise SystemExit"
    

    
def test_sync__dry_run():
    """
    Test option ``--dry-run`` of command ``sync``.
    The program must not change any repository.
    """
    #create project directory with configuration file and known bugs
    _, proj_dir, _ = setup_test_resources("sync_real_1")
    #go to project directory
    old_cwd = os.getcwd()
    os.chdir(proj_dir)
    #Get password from test framework
    addpw = {"trac":pytest.config.option.trac_password}
    
    now = datetime.utcnow()
    #Create Trac and Launchpad controllers
    tr_ctrl = TracController(example_conf.trac_data, authenticate=False)
    lp_ctrl = LpController(example_conf.lp_data, authenticate=True)
    #Change a bug in Launchpad
    text = "Changed by: `test_sync__dry_run` at {t}".format(t=now)
    idlp = ["939013"] #Sacred Test Bug Thirteen - modify me
    bug0, = lp_ctrl.get_bugs(idlp)
    bug0 = bug0._replace(description=text) #IGNORE:E1101
    lp_ctrl.update_bugs([bug0], idlp)
    
    #call synchronization algorithm with option ``--dry-run``
    sleep(2)
    tsync = datetime.utcnow()
    sleep(2)
    assert call_application_main("bsync sync --dry-run", addpw) == "0"
    
    #The synchronization must have changed no bugs.
    chlp = lp_ctrl.get_recent_changes(tsync)
    chtrac = tr_ctrl.get_recent_changes(tsync)
    assert len(chlp) == 0
    assert len(chtrac) == 0
    
    os.chdir(old_cwd)



def test_sync_new_1():
    """
    Create a bug in each repository and see if ``bsync`` creates it in 
    the other repository.
    """
    #create project directory with configuration file and known bugs
    _, proj_dir, _ = setup_test_resources("test_sync_new_1")
    #go to project directory
    old_cwd = os.getcwd()
    os.chdir(proj_dir)
    #Get password from test framework
    addpw = {"trac":pytest.config.option.trac_password}
    
    now = datetime.utcnow()
    #Create Trac and Launchpad controllers
    tr_ctrl = TracController(example_conf.trac_data, authenticate=True, 
                             addpw=addpw)
    lp_ctrl = LpController(example_conf.lp_data, authenticate=True)
    #Add test bug to Trac
    _, bug_tr, bug_lp = make_bugs()
    text0tr = "Test bug Trac - test_sync_new_1 - {t}".format(t=now)
    bug0tr = bug_tr._replace(summary=text0tr) #IGNORE:E1101
    tr_ctrl.create_bugs([bug0tr])
    #Add test bug to Launchpad
    text0lp = "Test bug LP - test_sync_new_1 - {t}".format(t=now)
    bug0lp = bug_lp._replace(title=text0lp) #IGNORE:E1101
    lp_ctrl.create_bugs([bug0lp])
    
    #synchronize the test repositories
    assert call_application_main("bsync sync", addpw) == "0"
    
    #Get the new bugs from Launchpad, test if both bugs are now on LP
    bugslp = lp_ctrl.get_recent_changes(now)
    textslp = [bug.title for bug in bugslp]
    print "textslp:"
    pprint(textslp)
    assert text0tr in textslp
    assert text0lp in textslp
    #Get the new bugs from Trac, test if both bugs are now on LP
    bugstrac = tr_ctrl.get_recent_changes(now)
    textstrac = [bug.summary for bug in bugstrac]
    print "textstrac:"
    pprint(textstrac)
    assert text0tr in textstrac
    assert text0lp in textstrac 
          
    os.chdir(old_cwd)



def test_sync_new_3():
    """
    Create bugs in both repositories. These bugs have the same title, but 
    different contents, they must be recognized as the same bug.
    """
    #create project directory with configuration file and known bugs
    _, proj_dir, _ = setup_test_resources("test_sync_new_3")
    #go to project directory
    old_cwd = os.getcwd()
    os.chdir(proj_dir)
    #Get password from test framework
    addpw = {"trac":pytest.config.option.trac_password}
    
    #Create Trac and Launchpad controllers
    tr_ctrl = TracController(example_conf.trac_data, authenticate=True, 
                             addpw=addpw)
    lp_ctrl = LpController(example_conf.lp_data, authenticate=True)
    #Add test bug to Launchpad and Trac
    t0 = datetime.utcnow()
    title = "Test bug - test_sync_new_3 - {t}".format(t=t0)
    _, bug_tr, bug_lp = make_bugs() 
    bug0t = bug_tr._replace(summary=title, description="Trac") #IGNORE:E1101
    bug0l = bug_lp._replace(title=title, description="Launchpad") #IGNORE:E1101
    idt = tr_ctrl.create_bugs([bug0t])
    idl = lp_ctrl.create_bugs([bug0l])
    
    #synchronize the test repositories
    assert call_application_main("bsync sync", addpw) == "0"
    
    #The bugs must now have same contents
    bug1t, = tr_ctrl.get_bugs(idt)
    bug1l, = lp_ctrl.get_bugs(idl)
    assert bug1t.summary == bug1l.title
    assert bug1t.description == bug1l.description

    os.chdir(old_cwd)



def test_sync_update_1():
    """
    Create a bug in each repository and see if ``bsync`` creates it in 
    the other repository.
    """
    #create project directory with configuration file and known bugs
    _, proj_dir, _ = setup_test_resources("test_sync_update_1")
    #go to project directory
    old_cwd = os.getcwd()
    os.chdir(proj_dir)
    #Get password from test framework
    addpw = {"trac":pytest.config.option.trac_password}
    
    now = datetime.utcnow()
    #Create Trac and Launchpad controllers
    tr_ctrl = TracController(example_conf.trac_data, authenticate=True,
                             addpw=addpw)
    lp_ctrl = LpController(example_conf.lp_data, authenticate=True)
    #Change a known bug in both repositories
    #Trac
    idtr0 = ["812"] #Sacred Test Bug Eleven - modify me
    bugtr, = tr_ctrl.get_bugs(idtr0) 
    text0tr = "Test text Trac - test_sync_update_1 - {t}".format(t=now)
    bugtr = bugtr._replace(description=text0tr) #IGNORE:E1101
    tr_ctrl.update_bugs([bugtr], idtr0)
    #Launchpad
    idlp0 = ["939010"] #Sacred Test Bug Twelve - modify me
    buglp, = lp_ctrl.get_bugs(idlp0)
    text0lp = "Test text LP - test_sync_update_1 - {t}".format(t=now)
    buglp = buglp._replace(description=text0lp) #IGNORE:E1101
    lp_ctrl.update_bugs([buglp], idlp0)
    
    sleep(2)
    #synchronize the test repositories
    assert call_application_main("bsync sync", addpw) == "0"
    
    #Get associated bugs from other repository, and see if they are updated  
    #Trac
    idtr = ["813"] #Sacred Test Bug Twelve - modify me
    bugtr, = tr_ctrl.get_bugs(idtr) 
    print text0lp
    print bugtr.description
    assert bugtr.description == text0lp
    #Launchpad
    idlp = ["935776"] #Sacred Test Bug Eleven - modify me
    buglp, = lp_ctrl.get_bugs(idlp)
    assert buglp.description == text0tr
    
    os.chdir(old_cwd)
    
    
    
def test_sync__since():
    """
    Test option ``--since`` of command ``sync``.
    The program must only consider changes after the specified time.
    """
    #create project directory with configuration file and known bugs
    _, proj_dir, _ = setup_test_resources("sync_real_1")
    #go to project directory
    old_cwd = os.getcwd()
    os.chdir(proj_dir)
    #Get password from test framework
    addpw = {"trac":pytest.config.option.trac_password}
    
    t0 = datetime.utcnow()
    #Create Trac and Launchpad controllers
    tr_ctrl = TracController(example_conf.trac_data, authenticate=False)
    lp_ctrl = LpController(example_conf.lp_data, authenticate=True)

    #Change a bug in Launchpad
    text = "Changed by: `test_sync__dry_run` at {t}".format(t=t0)
    idlp = ["939010"] #Sacred Test Bug Twelve - modify me
    bug0, = lp_ctrl.get_bugs(idlp)
    bug0 = bug0._replace(description=text) #IGNORE:E1101
    lp_ctrl.update_bugs([bug0], idlp)
    
    sleep(2)
    t1 = datetime.utcnow()
    sleep(2)
    #Later change an other bug in Launchpad
    text = "Changed by: `test_sync__dry_run` at {t}".format(t=t1)
    idlp = ["939013"] #Sacred Test Bug Thirteen - modify me
    bug0, = lp_ctrl.get_bugs(idlp)
    bug0 = bug0._replace(description=text) #IGNORE:E1101
    lp_ctrl.update_bugs([bug0], idlp)
    
    #call synchronization algorithm with option ``--since``
    sleep(2)
#    tsync = datetime.utcnow()
#    sleep(2)
    assert call_application_main("bsync sync --since " + t1.isoformat(), 
                                 addpw) == "0"
    
    #The synchronization must have changed only one bug
    #Not using ``tsync`` because it depends on the text merging algorithm if 
    #The bug is updated on Launchpad.
    chlp = lp_ctrl.get_recent_changes(t1)
    chtr = tr_ctrl.get_recent_changes(t1)
    assert len(chlp) == 1
    assert len(chtr) == 1
    assert chlp[0].description == text
    assert chtr[0].description == text
    
    os.chdir(old_cwd)



def test_sync__translate_links():
    """
    Test option ``--since`` of command ``sync``.
    The program must only consider changes after the specified time.
    """
    #create project directory with configuration file and known bugs
    _, proj_dir, _ = setup_test_resources("sync_real_1")
    #go to project directory
    old_cwd = os.getcwd()
    os.chdir(proj_dir)
    #Get password from test framework
    addpw = {"trac":pytest.config.option.trac_password}
    
    t0 = datetime.utcnow()
    #Create Trac and Launchpad controllers
    tr_ctrl = TracController(example_conf.trac_data, authenticate=False)
    lp_ctrl = LpController(example_conf.lp_data, authenticate=True)

    #Put bug-link into a bug in Launchpad
    text = textwrap.dedent(
    """
    Test translating bug links. (Text created at {time}.)
    The line below must contain a link to "Sacred Test Bug - Bug Link Two".
    Link to bug #941395 some more text.
    """).format(time=t0)
    idlp = ["941394"] #Sacred Test Bug - Bug Link One
    bug0lp, = lp_ctrl.get_bugs(idlp)
    bug0lp = bug0lp._replace(description=text) #IGNORE:E1101
    lp_ctrl.update_bugs([bug0lp], idlp)
        
    #call synchronization algorithm with option ``--since``
    sleep(2)
    assert call_application_main("bsync sync", addpw) == "0"
    
    #Test that Launchpad bug has not been messed up
    bug1lp, = lp_ctrl.get_bugs(idlp)
    #Original link text must exist
    assert bug1lp.description.find("bug #941395") != -1
    #No discovery link must be created
    assert bug1lp.description.find("BUGLINK") == -1
    os.chdir(old_cwd)

    #Test that trac bug has not been messed up
    idtr = ["810"] #Sacred Test Bug - Bug Link One
    bug1tr, = tr_ctrl.get_bugs(idtr)
    #Link must be translated
    assert bug1tr.description.find("bug #811") != -1
    #No discovery link must be created
    assert bug1tr.description.find("BUGLINK") == -1
    os.chdir(old_cwd)



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
    pytest.config.option.dist = "no"
    
#    setup_module(None)
#    teardown_module(None)
#    make_bugs()
#    test_sync__dry_run()
#    test_sync_new_1()
#    test_sync_new_3()
    test_sync_update_1()
#    test_sync__since()
#    test_sync__translate_links()
    
