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

from bug_syncer.repo_io import RepoControllerDummy, TracController, \
    LaunchpadController
from bug_syncer.common import TracData, LaunchpadData, DummyRepoData, \
    BugData, UserFatalError
import bug_syncer.example_conf as example_conf



def make_bugs():
    """Create bugs, that match the dummy task"""
    bug1 =  BugData(ids = {"SF-Trac":1}, 
                    time_created=datetime(2000, 1, 1), 
                    time_modified=datetime(2000, 2, 1), 
                    text_short=u"Test Bug One", 
                    text_long=u"Description of bug one.", 
                    reporter="Eike Welk", assigned_to="Eike Welk", 
                    status="new", priority="minor", resolution="none", kind="defect",
                    milestone="0.0.1")
    bug2 =  BugData(ids = {"SF-Trac":2}, 
                    time_created=datetime(2000, 1, 1), 
                    time_modified=datetime(2000, 2, 2), 
                    text_short=u"Test Bug Two", 
                    text_long=u"Description of bug two.", 
                    reporter="Eike Welk", assigned_to=None, 
                    status="new", priority="minor", resolution="none", kind="defect",
                    milestone="0.0.1")
    return bug1, bug2



def make_bugs_comparable(bug):
    "Set bug to neutral state, so that it can be compared."
    return bug._replace(ids={}, time_created=None, time_modified=None)



#---------------------- Test RepoControllerDummy -------------------------------
#==========================================================================

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
    repo.update_bugs([bug0m])
    repo.print_repo()
    
    #Get bugs that changed since we modified bug0 - only bug0 in modified form
    bugs = repo.get_recent_changes(tm)
    assert len(bugs) == 1
    assert make_bugs_comparable(bugs[0]) == make_bugs_comparable(bug0m)
    
    

def test__RepoControllerDummy__update_bugs():
    #Create repository
    repo_data = DummyRepoData(repo_name="repo_a", initial_bugs=[])
    repo = RepoControllerDummy(repo_data)
    #Create some bugs
    bug0, bug1 = make_bugs()
    #put bugs into repository
    bug_ids = repo.create_bugs([bug0, bug1])
    
    #Get bugs from repository (now IDs are correct for update method)
    bug0a, _ = repo.get_bugs(bug_ids)
    
    #Create modified bug
    bug0b = bug0a._replace(text_short="Modified Title")
    #Update bug in repository
    repo.update_bugs([bug0b])
    #Get changed bug from repository
    bug0c, _ = repo.get_bugs(bug_ids)
    #See if they have (mostly) the same contents.
    assert make_bugs_comparable(bug0b) == make_bugs_comparable(bug0c)
    
    #Repository must not update unknown bugs
    bug_bad0 = bug0._replace(ids={"foo":"bar"})
    with pytest.raises(KeyError):
        repo.update_bugs([bug_bad0])
        
    bug_bad1 = bug0._replace(ids={"repo_a":"bar"})
    with pytest.raises(KeyError):
        repo.update_bugs([bug_bad1])



#---------------------- Test TracController -------------------------------
#==========================================================================

def test_TracController_creation(): 
    """TracController: creation"""
    #Login without password - uses nonsense password "".
    trac_data = TracData(repo_name="SF-Trac", 
                         url="https://sourceforge.net/apps/trac/bug-repo-syncer/", 
                         user_name="eike", password="", comment="")
    TracController(trac_data)
    
    #Wrong url: raise error
    repo_data_wrong_URL = \
        trac_data._replace(url="http://sourceforge.net/apps/trac/wrong-repo-name/")
    with pytest.raises(UserFatalError):
        TracController(repo_data_wrong_URL)

    print "Test finished successfully, despite those many error messages."



def test_TracController__get_bugs(): 
    """TracController: get_bugs"""
    ctrl = TracController(example_conf.trac_data)
    bugs = ctrl.get_bugs([79, 82, 83]) #bugs are protected in: trac_delete_all_bugs
    
    for bug in bugs:
        print bug
    print
    
    assert len(bugs) == 3
    assert isinstance(bugs[0], BugData)
    
    

def test_TracController__get_bugs__with_translators(): 
    """TracController: get_bugs, complete example configuration"""
    #Test the complete example configuration for Trac
    ctrl = TracController(example_conf.trac_data,
                          people_translator=example_conf.people,
                          milestone_translator=example_conf.milestones)
    bugs = ctrl.get_bugs([79, 82, 83]) #bugs are protected in: trac_delete_all_bugs
    
    print "Trac bugs:"
    for bug in bugs:
        print bug
    print
    
    assert len(bugs) == 3
    assert isinstance(bugs[0], BugData)
    
    

def test_TracController__get_recent_changes(): 
    """TracController: get_recent_changes"""
    ctrl = TracController(example_conf.trac_data)
    bugs = ctrl.get_recent_changes(datetime(2012, 2, 22))
    
#    for bug in bugs:
#        print bug
#    print
    
#    #create list of test bugs
#    for bug in bugs:
#        if bug.text_short.startswith("Sacred"):
#            print '{id}, #{txt}'.format(id=bug.ids["SF-Trac"], txt=bug.text_short)
#    print
    
    #These bugs have all of Launchpad's bug statuses - and all of Trac's too.
    test_bug_ids = [82, #Sacred Test Bug One - LP: New
                    83, #Sacred Test Bug Two - LP: Incomplete
                    79, #Sacred Test Bug Three - LP: Opinion
                    118, #Sacred Test Bug Four - LP: Invalid
                    103, #Sacred Test Bug Five - LP: Won't Fix
                    101, #Sacred Test Bug Six - LP: Confirmed
                    128, #Sacred Test Bug Seven - LP: Triaged
                    119, #Sacred Test Bug Eight - LP: In Progress
                    129, #Sacred Test Bug Nine - LP: Fix Committed
                    130, #Sacred Test Bug Ten - LP: Fix Released
                    97, #Sacred Test Bug - no milestone
                    ]
    test_bugs = filter(lambda bug: bug.ids["SF-Trac"] in test_bug_ids, bugs) #IGNORE:W0141
        
    assert isinstance(bugs[0], BugData)
    assert len(test_bugs) == 11



def try_TracController__update_bugs():  
    """
    This test is not automatically executed in the test suite.
    It modifies the repository, and is not suited to be executed repeatedly.
    """
    #Create Trac controller that asks for password.
    trac_data = example_conf.trac_data._replace(password="ASK")
    ctrl = TracController(trac_data, True, example_conf.people, example_conf.milestones)

    #Create two bugs to update
    bug1, bug2 = make_bugs()
    
    #Update the bugs
    ctrl.update_bugs([bug1, bug2])



def try_TracController__create_bugs():  
    """
    This test is not automatically executed in the test suite.
    It modifies the repository, and is not suited to be executed repeatedly.
    """
    #Create Trac controler that asks for password.
    trac_data = example_conf.trac_data._replace(password="ASK")
    ctrl = TracController(trac_data, True, example_conf.people, example_conf.milestones)
    
    #Create two bugs to create
    bug1, bug2 = make_bugs()
    
    #Create the bugs
    bug_ids = ctrl.create_bugs([bug1, bug2])
    print list(bug_ids)



def try_TracController__delete_bugs(): 
    """
    This test is not automatically executed in the test suite.
    It modifies the repository, and is not suited to be executed repeatedly.
    """
    #Create Trac controler that asks for password.
    trac_data = example_conf.trac_data._replace(password="ASK")
    ctrl = TracController(trac_data, True, example_conf.people, example_conf.milestones)
    
    #Create one bug to delete
    bug1, _ = make_bugs()
    bug4 = bug1._replace(ids={"SF-Trac":4})
    
    #Delete the bugs
    ctrl.delete_bugs([bug4, 5])
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
    ctrl = TracController(repo_data=trac_data, 
                          authenticate=True, 
                          people_translator=example_conf.people, 
                          milestone_translator=example_conf.milestones)
    
    #Create one bug that we can recognize 
    bug1, _ = make_bugs()
    bug1 = bug1._replace(text_short="Test Bug - created at: " 
                                    + str(datetime.utcnow()),
                         text_long="Bug created by the test suite. \n"
                                   "It should be deleted automatically.")
    print "bug1:", bug1
    
    #create bug on server 
    bug_ids = ctrl.create_bugs([bug1])
    #read bug from server
    bug2 = ctrl.get_bugs(bug_ids)[0]
    print "bug2:", bug2
    
    #Test if we really got new bug back
    assert make_bugs_comparable(bug1) == make_bugs_comparable(bug2)

    #Modify the bug
    bug3 = bug2._replace(text_short="Modified " + bug2.text_short)
    print "bug3:", bug3
    #Modify bug on server
    ctrl.update_bugs([bug3])
    #read bug from server
    bug4 = ctrl.get_bugs(bug_ids)[0]
    print "bug4:", bug4
    
    #Test if we really got modified bug back
    assert make_bugs_comparable(bug3) == make_bugs_comparable(bug4)
    
    #Delete the bug
    ctrl.delete_bugs(bug_ids)
    #try to get bug - this must fail
    with pytest.raises(Exception):
        ctrl.get_bugs(bug_ids)
        
    print "Success!"



#------------------ Test LaunchpadController ------------------------------
#==========================================================================

def test_LaunchpadController_creation(): 
    """LaunchpadController: creation"""
    #Login without password
    launchpad_data = LaunchpadData(repo_name="Launchpad", 
                                   project_name="bug-repo-syncer",
                                   cachedir="/tmp/test/launchpadlib/cache/", 
                                   comment="")
    LaunchpadController(launchpad_data)
    

def test_LaunchpadController__get_bugs(): 
    """LaunchpadController: get_bugs"""
    ctrl = LaunchpadController(example_conf.lp_data)
    bugs = ctrl.get_bugs(['https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931634', 
                          'https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931663',   
                          'https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931665',
                          'https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931666',
                          'https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931704'])
    
    
    print "Launchpad bugs:"    
    for bug in bugs:
        print bug
    print
    
    assert len(bugs) == 5
    assert isinstance(bugs[0], BugData)
    
    
def test_LaunchpadController__get_bugs__with_translators(): 
    """LaunchpadController: get_bugs"""
    ctrl = LaunchpadController(example_conf.lp_data,  
                               people_translator=example_conf.people,
                               milestone_translator=example_conf.milestones)
    bugs = ctrl.get_bugs(['https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931634', 
                          'https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931663',   
                          'https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931665',
                          'https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931666',
                          'https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931704'])
    
    for bug in bugs:
        print bug
    print
    
    assert len(bugs) == 5
    assert isinstance(bugs[0], BugData)
    #TODO: more assertions look for all 8 test bugs.
    


def test_LaunchpadController__get_recent_changes(): 
    """LaunchpadController: get_bugs"""
    ctrl = LaunchpadController(example_conf.lp_data)
    #All "sacred" test bugs were changed after this date
    bugs = ctrl.get_recent_changes(datetime(2012, 2, 22))
    
#    for bug in bugs:
#        print bug
#    print
   
#    #create list of test bugs
#    for bug in bugs:
#        if bug.text_short.startswith("Sacred"):
#            print '"{id}", #{txt}'.format(id=bug.ids["Launchpad"], txt=bug.text_short)
#    print
    
    #See if the "sacred" test bugs are all in the response
    test_bug_ids = [
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931634", #Sacred Test Bug One - LP: New
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931663", #Sacred Test Bug Two - LP: Incomplete
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931665", #Sacred Test Bug Three - LP: Opinion
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/932082", #Sacred Test Bug Four - LP: Invalid
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/931666", #Sacred Test Bug Five - LP: Won't Fix
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/934181", #Sacred Test Bug Six - LP: Confirmed
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/934666", #Sacred Test Bug Seven - LP: Triaged
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/934638", #Sacred Test Bug Eight - LP: In Progress
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/934672", #Sacred Test Bug Nine - LP: Fix Committed
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/934674", #Sacred Test Bug Ten - LP: Fix Released
        "https://api.launchpad.net/1.0/bug-repo-syncer/+bug/932081", #Sacred Test Bug - no milestone
        ]
    test_bugs = filter(lambda bug: bug.ids["Launchpad"] in test_bug_ids, bugs) #IGNORE:W0141
    
    assert isinstance(bugs[0], BugData)
    assert len(bugs) > 11
    assert len(test_bugs) == 11



def try_LaunchpadController__update_bugs():  
    """
    This test is not automatically executed in the test suite.
    It modifies the repository, and is not suited to be executed repeatedly.
    """
    #Create Launchpad controller that asks for password.
    launchpad_data = example_conf.lp_data._replace(authenticate=True)
    ctrl = LaunchpadController(launchpad_data, True,
                               example_conf.people, example_conf.milestones)

    #Create a bug that really exists in Launchpad
    bug1, _ = make_bugs()
    bug1 = bug1._replace(ids={"Launchpad":"https://api.launchpad.net/1.0/bug-repo-syncer/+bug/934181"},
                         text_long="Changed by 'try_LaunchpadController__update_bugs' at: {t}."
                                   .format(t=datetime.utcnow()))
    
    #Update the bugs
    ctrl.update_bugs([bug1])
    
    #Go to Launchpad to see it:
    #    https://bugs.launchpad.net/bug-repo-syncer/+bug/934181
    print "Finished."



def test_LaunchpadController__create_bugs():  
    """
    Create locally, create it on Launchpad, download it, and compare it to 
    the original bug, to see if we really got our bug back.
    
    This test is normally skipped in the test suite.
    It creates a bug in Launchpad which can not be deleted. It is therefore 
    not suited to be executed repeatedly.    
    """
    if not pytest.config.option.add_bugs_to_launchpad:
        pytest.skip("Launchpad: Bug creation, reading. Adds Bug to LP that "
                    "can not be removed.")
    
    #Create Launchpad controller that asks for password.
    ctrl = LaunchpadController(repo_data=example_conf.lp_data, 
                               authenticate=True,
                               people_translator=example_conf.people, 
                               milestone_translator=example_conf.milestones)
    
    #Create one bug that we can recognize 
    bug1, _ = make_bugs()
    bug1 = bug1._replace(text_short="Test Bug - created at: " + str(datetime.utcnow()),
                         text_long="Created by 'test_LaunchpadController__create_bugs' at: {t}."
                                   .format(t=datetime.utcnow()),
                         status="closed", 
                         resolution="invalid")
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
    
    Bug creation -> reading -> updating -> reading -> updating as "Fix Released" 
    
    This test is normally skipped in the test suite.
    It creates a bug in Launchpad which can not be deleted. It is therefore 
    not suited to be executed repeatedly.    
    """
    
    if not pytest.config.option.modify_launchpad:
        pytest.skip("Launchpad: Bug reading, updating, "
                    "set status and resolution.")
    
    #Create Launchpad controller that asks for password.
    ctrl = LaunchpadController(repo_data=example_conf.lp_data, 
                               authenticate=True,
                               people_translator=example_conf.people, 
                               milestone_translator=example_conf.milestones)
    
    #A bug that we can modify: Sacred Test Bug Eleven - modify me
    id_list = ["https://api.launchpad.net/1.0/bug-repo-syncer/+bug/935776"] 

    #Get the bug from Launchpad
    bug0 = ctrl.get_bugs(id_list)[0]
    print "bug0: ", bug0

    #Modify the bug
    bugm1 = bug0._replace(text_short="Modified " + bug0.text_short,
                          status="confirmed", resolution="none")
    print "bugm1: ", bugm1
    #Modify bug on server
    ctrl.update_bugs([bugm1])
    #read bug from server
    bugm2 = ctrl.get_bugs(id_list)[0]
    print "bugm2: ", bugm2
    
    #Test if we really got modified bug back
    assert make_bugs_comparable(bugm1) == make_bugs_comparable(bugm2)
    #Test if it was really modified
    assert make_bugs_comparable(bug0) != make_bugs_comparable(bugm2)
    #Test some concrete facts
    assert bugm2.status == "confirmed"
    assert bugm2.resolution == "none"
    
    #Reset bug back to initial state, but keep the text
    ctrl.update_bugs([bug0])
    
    #Go to Launchpad to see it:
    #    https://bugs.launchpad.net/bug-repo-syncer/+milestone/0.0.1
    print "Success!"



if __name__ == '__main__':
    #The tests use those objects to see if they should be skipped or executed
    #The test runner ``py.test`` creates these objects normally.
    #pylint: disable=W0201
    class Dummy(object): pass
    pytest.config = Dummy()
    pytest.config.option = Dummy()
    pytest.config.option.dangerous_time_consuming = True
    pytest.config.option.modify_launchpad = True
    pytest.config.option.add_bugs_to_launchpad = True
    pytest.config.option.modify_trac = True
    pytest.config.option.trac_password = "ASK"
    
#    test__RepoControllerDummy__create_bugs()
#    test__RepoControllerDummy__get_bugs()
    test__RepoControllerDummy__get_recent_changes()
#    test__RepoControllerDummy__update_bugs()

#    test_TracController_creation()
#    test_TracController__get_bugs()
#    test_TracController__get_bugs__with_translators()
#    test_TracController__get_recent_changes()
#    try_TracController__update_bugs()
#    try_TracController__delete_bugs()
#    try_TracController__create_bugs()

#    test_TracController__modify_repository()
#    test_LaunchpadController_creation()
#    test_LaunchpadController__get_bugs()
#    test_LaunchpadController__get_bugs__with_translators()
#    test_LaunchpadController__get_recent_changes()
#    try_LaunchpadController__update_bugs()
#    try_LaunchpadController__create_bugs()
#    test_LaunchpadController__delete_bugs()
#    test_LaunchpadController__modify_repository()
    pass #pylint: disable=W0107
