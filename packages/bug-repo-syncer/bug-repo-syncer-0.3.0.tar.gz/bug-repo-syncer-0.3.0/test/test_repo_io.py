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
Tests for module repo_io
"""

#pylint: disable=W0212,E1101

from __future__ import division
from __future__ import absolute_import              

import pytest #contains `skip`, `fail`, `raises`, `config`

from datetime import datetime
from time import sleep
#from random import random

from test.helpers import make_bugs_comparable

from bug_repo_syncer.repo_io import RepoControllerDummy, \
    TracController, BugTrac, bugtrac_equal_contents, BugTracFilter, \
    LpController, BugLp, buglp_equal_contents, BugLpFilter
from bug_repo_syncer.common import TracData, LaunchpadData, DummyRepoData, \
    BugIntl, UserFatalError, EquivalenceTranslator, equal_contents
import bug_repo_syncer.example_conf as example_conf



#---------------------- Test RepoControllerDummy -------------------------------
#==========================================================================

def make_bugs():
    """Create bugs"""
    bug1 =  BugIntl(repo_name="repo_a", id="a0",
                    time_created=datetime(2000, 1, 1), 
                    time_modified=datetime(2000, 2, 1), 
                    text_short=u"Test Bug Zero", 
                    text_long=u"Description of bug zero.", 
                    reporter="Eike Welk", assigned_to="Eike Welk", 
                    status="new", priority="minor", resolution="none", 
                    kind="defect",
                    milestone="0.0.1")
    bug2 =  BugIntl(repo_name="repo_a", id="a1",
                    time_created=datetime(2000, 1, 1), 
                    time_modified=datetime(2000, 2, 2), 
                    text_short=u"Test Bug One", 
                    text_long=u"Description of bug one.", 
                    reporter="Eike Welk", assigned_to=None, 
                    status="new", priority="minor", resolution="none", 
                    kind="defect",
                    milestone="0.0.1")
    return bug1, bug2



def test__RepoControllerDummy__create_bugs():
    #Create repository
    repo_data = DummyRepoData(repo_name="repo_a", initial_bugs=[])
    repo = RepoControllerDummy(repo_data)
    #Create some bugs
    bug1, bug2 = make_bugs()
    
    ids = repo.create_bugs([bug1, bug2])
    print ids
    
    assert len(ids) == 2
    assert repo.num_created == 2
    


def test__RepoControllerDummy__get_bugs():
    #Create repository
    repo_data = DummyRepoData(repo_name="repo_a", initial_bugs=[])
    repo = RepoControllerDummy(repo_data)
    #Create some bugs
    bug0, bug1 = make_bugs()
    #put bugs into repository
    ids = repo.create_bugs([bug0, bug1])
    
    #try to get bugs from the repository
    bug0a, bug1a = repo.get_bugs(ids)
    
    print bug0
    print bug0a
    #The repository may change times and ID, but the other data must be unchanged
    assert make_bugs_comparable(bug0a) == make_bugs_comparable(bug0)
    #The repository must allocate its own data.
    assert bug0a is not bug0
    
    assert make_bugs_comparable(bug1a) == make_bugs_comparable(bug1)
    assert bug1a is not bug1
    
    #getting the bugs twice must return entirely different bugs, so that we can 
    #manipulate their mutable attributes
    bug0b = repo.get_bugs(ids)[0]
    bug0c = repo.get_bugs(ids)[0]
    
    assert bug0b == bug0c
    assert bug0b is not bug0c



def test__RepoControllerDummy__get_recent_changes(): 
    #Create repository
    repo_data = DummyRepoData(repo_name="repo_a", initial_bugs=[])
    repo = RepoControllerDummy(repo_data)
    #Create some bugs
    bug0, bug1 = make_bugs()
    
    #put bug 0 into repository first
    t0 = datetime.utcnow()
    id0, = repo.create_bugs([bug0])
    repo.print_repo()
    #put bug 1 into repository later
    sleep(0.1)
    t1 = datetime.utcnow()
    _ = repo.create_bugs([bug1])
    repo.print_repo()
    
    #Get bugs that changed since we started to use the repository - all bugs
    bugs = repo.get_recent_changes(t0)
    assert len(bugs) == 2
    #Get bugs that changed since we created bug1 - must be only bug1
    bugs = repo.get_recent_changes(t1)
    assert len(bugs) == 1
    assert make_bugs_comparable(bugs[0]) == make_bugs_comparable(bug1)
    
    #Change bug 0 even later
    sleep(0.1)
    tm = datetime.utcnow()
    bug0g, = repo.get_bugs([id0])
    bug0m = bug0g._replace(text_short="New title for bug 0")
    repo.update_bugs([bug0m], [id0])
    repo.print_repo()
    
    #Get bugs that changed since we modified bug0 - only bug0 in modified form
    bugs = repo.get_recent_changes(tm)
    assert len(bugs) == 1
    assert make_bugs_comparable(bugs[0]) == make_bugs_comparable(bug0m)
    
    

def test__RepoControllerDummy__update_bugs():
    #Create some bugs
    bug0, bug1 = make_bugs()
    #Create repository with some initial bugs
    repo_data = DummyRepoData(repo_name="repo_a", initial_bugs=[bug0, bug1])
    repo = RepoControllerDummy(repo_data)

    
    #Create modified bug
    bug0b = bug0._replace(text_short="Modified Title")
    #Update bug in repository
    broken = repo.update_bugs([bug0b], ["a0"])
    assert len(broken) == 0
    #Get changed bug from repository
    bug0c, = repo.get_bugs(["a0"])
    #See if they have (mostly) the same contents.
    assert equal_contents(bug0b, bug0c)

    bug0c = bug0._replace(text_short="One More Bug")
    
    #try to update bug that does not exist
    broken = repo.update_bugs([bug0c], ["2"])
#    print broken
    assert len(broken) == 1
    assert equal_contents(bug0c, broken[0])



#---------------------- Test TracController -------------------------------
#==========================================================================

def test_TracController_creation(): 
    """TracController: creation"""
    #Login into test Trac anonymously
    login = TracData(repo_name="trac", 
                     url="http://sourceforge.net/apps/trac/repo-syncer-tst", 
                     user_name="eike", password="", comment="")
    TracController(login)
    
    #Log in to test Trac with password if the user supplied a password.
    if pytest.config.option.modify_trac:
        login = login._replace(password=pytest.config.option.trac_password)
        TracController(login, authenticate=True)
    
    #Login into real Trac anonymously
    login = TracData(repo_name="trac", 
                         url="https://sourceforge.net/apps/trac/bug-repo-syncer", 
                         user_name="eike", password="", comment="")
    TracController(login)
    
    #Wrong url: raise error
    repo_data_wrong_URL = login._replace(
                url="http://sourceforge.net/apps/trac/no-existing-repo-name")
    with pytest.raises(UserFatalError):
        TracController(repo_data_wrong_URL)

    print "Test finished successfully."



def test_TracController__get_bugs(): 
    """TracController: get_bugs"""
    ctrl = TracController(example_conf.trac_data)
    bugs = ctrl.get_bugs(["800", #Sacred Test Bug - LP: New
                          "801", #Sacred Test Bug - LP: Incomplete
                          "802", #Sacred Test Bug - LP: Opinion
                          ]) #bugs are protected in: trac_delete_all_bugs
    
    for bug in bugs:
        print bug
    print
    
    assert len(bugs) == 3
    assert isinstance(bugs[0], BugTrac)
    
    

def test_TracController__get_recent_changes(): 
    """TracController: get_recent_changes"""
    ctrl = TracController(example_conf.trac_data)
    bugs = ctrl.get_recent_changes(datetime(1970, 1, 1))
    
#    for bug in bugs:
#        print bug
#    print
    
    #These are special test bugs, that should not be deleted
    test_bug_ids = ["800", #Sacred Test Bug - Status LP: New
                    "801", #Sacred Test Bug - Status LP: Incomplete
                    "802", #Sacred Test Bug - Status LP: Opinion
                    "803", #Sacred Test Bug - Status LP: Invalid
                    "804", #Sacred Test Bug - Status LP: Won't Fix
                    "805", #Sacred Test Bug - Status LP: Confirmed
                    "806", #Sacred Test Bug - Status LP: Triaged
                    "807", #Sacred Test Bug - Status LP: In Progress
                    "808", #Sacred Test Bug - Status LP: Fix Committed
                    "809", #Sacred Test Bug - Status LP: Fix Released
                    "810", #Sacred Test Bug - Bug Link One
                    "811", #Sacred Test Bug - Bug Link Two
                    "812", #Sacred Test Bug Eleven - modify me
                    "813", #Sacred Test Bug Twelve - modify me
                    "814", #Sacred Test Bug Thirteen - modify me
                    "815", #Sacred Test Bug - no milestone                           
                    ]
    test_bugs = filter(lambda bug: bug.id in test_bug_ids, bugs) #IGNORE:W0141
        
    assert all([isinstance(bug, BugTrac) for bug in bugs])
    assert len(bugs) > 16
    assert len(test_bugs) == 16



def test_TracController__update_bugs():  
    """
    This test is not automatically executed in the test suite.
    It modifies the repository, and is not suited to be executed repeatedly.
    """
    if pytest.config.option.modify_trac:
        trac_password = pytest.config.option.trac_password
        addpw = {"trac":trac_password}
    else:
        pytest.skip("Trac: Test updating bugs. No password given.")

    #Create Trac controller that logs in with password.
    ctrl = TracController(example_conf.trac_data, 
                          authenticate=True, addpw=addpw)

    #Create a bug that really exists in Launchpad
    bug1 = make_bugs_trac()
    bug1 = bug1._replace(
        summary = "Sacred Test Bug Eleven - modify me",
        description="Changed by `test_TracController__update_bugs` at: {t}."
                    .format(t=datetime.utcnow()))
    #Update the bug: Sacred Test Bug Eleven - modify me 
    broken = ctrl.update_bugs([bug1], ["812"])
    assert len(broken) == 0
    #Go to Trac to see it:
    #    http://sourceforge.net/apps/trac/repo-syncer-tst/ticket/812
    
    bug2 = bug1._replace(summary = "Test Bug for bug-repo-syncer")
    
    #try to update bug that does not exist
    broken = ctrl.update_bugs([bug2, bug1], ["2", "812"])
#    print broken
    assert len(broken) == 1
    assert bugtrac_equal_contents(bug2, broken[0])

    print "Finished."



def try_TracController__create_bugs():  
    """
    This test is not automatically executed in the test suite.
    It modifies the repository, and is not suited to be executed repeatedly.
    """
    #Create Trac controler that asks for password.
    trac_data = example_conf.trac_data._replace(password=None)
    ctrl = TracController(trac_data, True)
    
    #Create two bugs to create
    bug1 = make_bugs_trac()
    
    #Create the bugs
    bug_ids = ctrl.create_bugs([bug1])
    print list(bug_ids)



def try_TracController__delete_bugs(): 
    """
    This test is not automatically executed in the test suite.
    It modifies the repository, and is not suited to be executed repeatedly.
    """
    #Create Trac controler that asks for password.
    trac_data = example_conf.trac_data._replace(password=None)
    ctrl = TracController(trac_data, True)

    #Delete the bugs
    ctrl.delete_bugs([5])
#    ctrl.delete_bugs([12, 13, 14, 15])



def test_TracController__modify_repository(): 
    """
    Sustainable test for operations that modify the Trac repository:
    
    Bug creation -> reading -> updating -> reading -> deletion 
    """
    if pytest.config.option.modify_trac:
        trac_password = pytest.config.option.trac_password
    else:
        pytest.skip("Trac: Bug creation, reading, updating, reading, "
                    "deletion. No password given.")
    
    #Create Trac controler that knows the right password.
    trac_data = example_conf.trac_data._replace(password=trac_password)
    ctrl = TracController(repo_data=trac_data, authenticate=True)
    
    #Create one bug that we can recognize 
    bug1 = make_bugs_trac()
    bug1 = bug1._replace(summary="Test Bug - created at: " 
                                 + str(datetime.utcnow()),
                         description="Bug created by the test suite. \n"
                                     "It should be deleted automatically.")
    print "bug1:", bug1
    
    #create bug on server 
    bid, = ctrl.create_bugs([bug1])
    #read bug from server
    bug2, = ctrl.get_bugs([bid])
    print "bug2:", bug2
    
    #Test if we really got new bug back
    assert make_bugs_comparable(bug1) == make_bugs_comparable(bug2)

    #Modify the bug
    bug3 = bug2._replace(summary="Modified " + bug2.summary)
    print "bug3:", bug3
    #Modify bug on server
    ctrl.update_bugs([bug3], [bid])
    #read bug from server
    bug4, = ctrl.get_bugs([bid])
    print "bug4:", bug4
    
    #Test if we really got modified bug back
    assert make_bugs_comparable(bug3) == make_bugs_comparable(bug4)
    
    #Delete the bug
    ctrl.delete_bugs([bid])
    #try to get bug - this must fail
    with pytest.raises(Exception):
        ctrl.get_bugs([bid])
        
    print "Success!"



def make_bugs_trac():
    """Create Trac bug"""
    bug0 =  BugTrac(repo_name="trac", id=0,
                    time_created=datetime(2000, 1, 1), 
                    time_modified=datetime(2000, 2, 1), 
                    summary=u"Test Bug Zero", 
                    description=u"Description of bug zero.", 
                    reporter="Eike Welk", owner="Eike Welk", 
                    status="new", priority="minor", 
                    resolution="none", type="defect",
                    milestone="0.0.1")
    return bug0



def test_bugtrac_equal_contents():
    """
    Test comparison function for Trac bugs.
    """ 
    bug0 = make_bugs_trac()
    #All these fields must be ignored when testing for equal contents
    bug1 = bug0._replace(repo_name="foo", id=2, 
                         time_created=datetime(2010, 10, 10), 
                         time_modified=datetime(2010, 10, 10))
    #This field is important for comparing contents
    bug2 = bug0._replace(summary="foo")
    
    assert bugtrac_equal_contents(bug0, bug1)
    assert not bugtrac_equal_contents(bug0, bug2)
    
    
    
def test_BugTracFilter():
    """
    Test conversion of Trac bugs to internal bugs.
    
    The conversion is fairly trivial, not much testing necessary.
    """
    btf = BugTracFilter()
    
    bug0 = make_bugs_trac()
    
    #Convert Trac bug to internal bug
    bug_i = btf.repo2intl(bug0)
    assert isinstance(bug_i, BugIntl)
    assert bug_i.text_short == bug0.summary
    assert bug_i.text_long == bug0.description
    assert bug_i.assigned_to == bug0.owner
    
    #Convert internal bug to Trac bug
    bug_tr = btf.intl2repo(bug_i)
    assert isinstance(bug_tr, BugTrac)
    assert bug_tr == bug0
    
    
    
#------------------ Test LpController ------------------------------
#==========================================================================

def test_LaunchpadController_creation(): 
    """LpController: creation"""
    #Login without password into test server
    launchpad_data = LaunchpadData(repo_name="lp", 
                                   project_name="bug-repo-syncer",
                                   cachedir=None,
                                   server="staging",
                                   comment="")
    LpController(launchpad_data)
    
    #Login without password into real server
    launchpad_data = LaunchpadData(repo_name="lp", 
                                   project_name="bug-repo-syncer",
                                   cachedir=None,
                                   server="production",
                                   comment="")
    LpController(launchpad_data)
    
    #Try to login with nonsense name must produce error
    launchpad_data = LaunchpadData(repo_name="lp", 
                                   project_name="project-does-not-exist",
                                   cachedir=None,
                                   server="production",
                                   comment="")
    with pytest.raises(UserFatalError):
        LpController(launchpad_data)



def test_LaunchpadController__get_bugs(): 
    """LpController: get_bugs - download bugs by their ID"""
    ctrl = LpController(example_conf.lp_data)
    bugs = ctrl.get_bugs([    
        "931634", #Sacred Test Bug - LP: New
        "931663", #Sacred Test Bug - LP: Incomplete
        "931665", #Sacred Test Bug - LP: Opinion
        ])
    
    print "Launchpad bugs:"    
    for bug in bugs:
        print bug
    print
    
    assert len(bugs) == 3
    assert isinstance(bugs[0], BugLp)
    assert bugs[0].id == "931634"
    
    with pytest.raises(KeyError):
        #This bug really exists, but it is not in 'bug-repo-syncer'
        bugs = ctrl.get_bugs([123]) 
        print bugs #Should not be executed
    
    
    
def test_LaunchpadController__get_recent_changes(): 
    """Test ``LpController.get_recent_changes``"""
    
    if not (pytest.config.option.slow_and_dangerous):
        pytest.skip("This is a very time consuming test.") #IGNORE:E1101
        
    ctrl = LpController(example_conf.lp_data)
    bugs = ctrl.get_recent_changes(datetime(1970, 1, 1))
    
#    for bug in bugs:
#        print bug
#    print
    
    #See if the "sacred" test bugs are all in the response
    test_bug_ids = [
            "931634", #Sacred Test Bug - Status LP: New
            "931663", #Sacred Test Bug - Status LP: Incomplete
            "931665", #Sacred Test Bug - Status LP: Opinion
            "932082", #Sacred Test Bug - Status LP: Invalid
            "931666", #Sacred Test Bug - Status LP: Won't Fix
            "934181", #Sacred Test Bug - Status LP: Confirmed
            "934666", #Sacred Test Bug - Status LP: Triaged
            "934638", #Sacred Test Bug - Status LP: In Progress
            "934672", #Sacred Test Bug - Status LP: Fix Committed
            "934674", #Sacred Test Bug - Status LP: Fix Released
            "941394", #Sacred Test Bug - Bug Link One
            "941395", #Sacred Test Bug - Bug Link Two
            "935776", #Sacred Test Bug Eleven - modify me
            "939010", #Sacred Test Bug Twelve - modify me
            "939013", #Sacred Test Bug Thirteen - modify me
            "932081", #Sacred Test Bug - no milestone                      
        ]
    filt_bug_ids = [bug.id for bug in bugs if bug.id in test_bug_ids]
    
    print set(test_bug_ids).difference(filt_bug_ids) #prints set(['931663'])
    
    assert isinstance(bugs[0], BugLp)
    assert len(bugs) >= 16
    pytest.xfail("Possible bug in Launchpadlib ``project.searchTasks``.")
    assert len(filt_bug_ids) == len(test_bug_ids) 



def test_LaunchpadController__get_recent_changes__fast(): 
    """
    Test ``LpController.get_recent_changes`` 
    Fast test, that modifies bugs on Launchpad
    """
    if not (pytest.config.option.modify_launchpad):
        pytest.skip("This test modifies Launchpad.") #IGNORE:E1101
        
    now = datetime.utcnow()
    test_bug_ids = [
            "935776", #Sacred Test Bug Eleven - modify me
            "939010", #Sacred Test Bug Twelve - modify me
            "939013", #Sacred Test Bug Thirteen - modify me
        ]
    
    #Create a controller with write access
    ctrl = LpController(example_conf.lp_data, authenticate=True)
    #Modify some bugs
    bugs = ctrl.get_bugs(test_bug_ids)
    msg = ("Changed at {t} by \n" 
           "test_LaunchpadController__get_recent_changes__fast".format(t=now))
    bugsm = [bug._replace(description=msg) for bug in bugs]
    ctrl.update_bugs(bugsm, test_bug_ids)
    
    #Get the changes since the test is started.
    bugs_changed = ctrl.get_recent_changes(now)
    
    print "Changed bugs:"
    for bug in bugs_changed:
        print bug
    
    #``get_recent_changes`` must return all bugs that were modified here.
    assert len(bugs_changed) >= 3
    ids_changed = [bug.id for bug in bugs_changed]
    assert set(ids_changed).issuperset(set(test_bug_ids))
    
    

def test_LaunchpadController__update_bugs():  
    """
    Test ``LpController.update_bugs``, modify existing bug
    """
    if not pytest.config.option.modify_trac:
        pytest.skip("Launchpad: Test updating bugs. No password given.")

    #Create Launchpad controller that asks for password.
    ctrl = LpController(example_conf.lp_data, authenticate=True)

    #Create a bug that really exists in Launchpad
    bug1 = make_bugs_lp()
    bug1 = bug1._replace(
        title = "Sacred Test Bug Eleven - modify me",
        description="Changed by 'test_LaunchpadController__update_bugs' at: {t}."
                    .format(t=datetime.utcnow()))
    #Update the bug: Sacred Test Bug Eleven - modify me 
    broken = ctrl.update_bugs([bug1], ["935776"])
    assert len(broken) == 0
    #Go to Launchpad to see it:
    #    https://bugs.qastaging.launchpad.net/bug-repo-syncer/+bug/935776
    
    bug2 = bug1._replace(title = "Test Bug for bug-repo-syncer")
    
    #try to update bug that does not exist
    broken = ctrl.update_bugs([bug2], ["2"])
    print broken
    assert len(broken) == 1
    assert buglp_equal_contents(bug2, broken[0])

    #try to update bug that is not in bug-repo-syncer
    broken = ctrl.update_bugs([bug2], ["4"])
    print broken
    assert len(broken) == 1
    assert buglp_equal_contents(bug2, broken[0])

    print "Finished."



def test_LaunchpadController__create_bugs():  
    """
    Create locally, create it on Launchpad, download it, and compare it to 
    the original bug, to see if we really got our bug back.
    
    This test is normally skipped in the test suite.
    It creates a bug in Launchpad which can not be deleted. It is therefore 
    not suited to be executed repeatedly.    
    """
    if not pytest.config.option.modify_launchpad:
        pytest.skip("Launchpad: Bug creation, reading.")
    
    #Create Launchpad controller that asks for password.
    ctrl = LpController(repo_data=example_conf.lp_data, authenticate=True)
    
    #Create one bug that we can recognize 
    now = str(datetime.utcnow())
    bug1 = make_bugs_lp()
    bug1 = bug1._replace(title="Test Bug - created at: " + now,
                         description="Created by 'test_LaunchpadController__create_bugs' at: {t}."
                                     .format(t=now),
                         status="Invalid")
    print "bug1: ", bug1
    
    #create bug on server 
    bug_ids = ctrl.create_bugs([bug1])
    #read bug from server
    bug2 = ctrl.get_bugs(bug_ids)[0]
    print "bug2: ", bug2
    
    #Test if we really got new bug back
    assert make_bugs_comparable(bug1) == make_bugs_comparable(bug2)



def test_LaunchpadController__modify_repository(): 
    """
    Test for operations that modify the Launchpad repository:
    
    Bug reading -> updating -> reading -> updating as "Fix Released" 
    
    This test is normally skipped in the test suite.
    It creates a bug in Launchpad which can not be deleted. It is therefore 
    not suited to be executed repeatedly.    
    """
    
    if not pytest.config.option.modify_launchpad:
        pytest.skip("Launchpad: Bug reading, updating, "
                    "set status and resolution.")
    
    #Create Launchpad controller that asks for password.
    ctrl = LpController(repo_data=example_conf.lp_data, authenticate=True)
    
    #A bug that we can modify: Sacred Test Bug Twelve - modify me
    id0 = "939010" #Sacred Test Bug Twelve - modify me 

    #Get the bug from Launchpad
    bug0, = ctrl.get_bugs([id0])
    print "bug0: ", bug0

    #Modify the bug
    bugm1 = bug0._replace(description="Modified " + bug0.description,
                          status="Confirmed", importance="Medium")
    print "bugm1: ", bugm1
    #Modify bug on server
    ctrl.update_bugs([bugm1], [id0])
    #read bug from server
    bugm2, = ctrl.get_bugs([id0])
    print "bugm2: ", bugm2
    
    #Test if we really got modified bug back
    assert make_bugs_comparable(bugm1) == make_bugs_comparable(bugm2)
    #Test if it was really modified
    assert make_bugs_comparable(bug0) != make_bugs_comparable(bugm2)
    #Test some concrete facts
    assert bugm2.status == "Confirmed"
    assert bugm2.importance == "Medium"
    
    #Reset bug back to initial state
    ctrl.update_bugs([bug0], [id0])
    
    #Go to Launchpad to see it:
    #    https://bugs.launchpad.net/bug-repo-syncer/+milestone/0.0.1
    print "Success!"



def make_bugs_lp():
    """Create Launchpad bug"""
    bug0 =  BugLp(repo_name="lp", id=0,
                    time_created=datetime(2000, 1, 1), 
                    time_modified=datetime(2000, 2, 1), 
                    title=u"Test Bug Zero", 
                    description=u"Description of bug zero.", 
                    owner="eike-welk", assignee="eike-welk", 
                    status="New", importance="Medium", 
                    milestone="0.0.1")
    return bug0



def test_buglp_equal_contents():
    """
    Test comparison function for Trac bugs.
    """ 
    bug0 = make_bugs_lp()
    #All these fields must be ignored when testing for equal contents
    bug1 = bug0._replace(repo_name="foo", id=2, 
                         time_created=datetime(2010, 10, 10), 
                         time_modified=datetime(2010, 10, 10))
    #This field is important for comparing contents
    bug2 = bug0._replace(title="foo")
    
    assert buglp_equal_contents(bug0, bug1)
    assert not buglp_equal_contents(bug0, bug2)
    
    
    
def test_BugLpFilter():
    """
    Test conversion of Trac bugs to internal bugs.
    
    TODO: Test the status conversion.
    """
    blpf = BugLpFilter()
    
    bug0 = make_bugs_lp()
    
    #Convert Trac bug to internal bug
    bug_i = blpf.repo2intl(bug0)
    assert isinstance(bug_i, BugIntl)
    assert bug_i.text_short == bug0.title
    assert bug_i.text_long == bug0.description
    assert bug_i.assigned_to == bug0.assignee
    
    #Convert internal bug to Trac bug
    bug_tr = blpf.intl2repo(bug_i)
    assert isinstance(bug_tr, BugLp)
    assert bug_tr == bug0



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
    
#    test__RepoControllerDummy__create_bugs()
#    test__RepoControllerDummy__get_bugs()
#    test__RepoControllerDummy__get_recent_changes()
    test__RepoControllerDummy__update_bugs()

#    test_TracController_creation()
#    test_TracController__get_bugs()
#    test_TracController__get_bugs__with_translators()
#    test_TracController__get_recent_changes()
#    test_TracController__update_bugs()
#    try_TracController__delete_bugs()
#    try_TracController__create_bugs()
#    test_TracController__modify_repository()
#    test_bugtrac_equal_contents()
#    test_BugTracFilter()

#    test_LaunchpadController_creation()
#    test_LaunchpadController__get_bugs()
#    test_LaunchpadController__get_bugs__with_translators()
#    test_LaunchpadController__get_recent_changes()
#    test_LaunchpadController__get_recent_changes__fast()
#    test_LaunchpadController__update_bugs()
#    test_LaunchpadController__create_bugs()
#    test_LaunchpadController__modify_repository()
#    test_buglp_equal_contents()
#    test_BugLpFilter()
