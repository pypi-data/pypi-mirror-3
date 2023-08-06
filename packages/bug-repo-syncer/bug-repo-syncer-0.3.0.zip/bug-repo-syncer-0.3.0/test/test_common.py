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
Tests for module common
"""

#pylint: disable=W0212,E1101

from __future__ import division
from __future__ import absolute_import              

import pytest #contains `skip`, `fail`, `raises`, `config`

from pprint import pprint 

from bug_repo_syncer.common import BugIntl, \
    UserFatalError, UnknownRepoError, UnknownWordError, \
    EquivalenceTranslator, BugLinkTranslator, PeopleMilestoneFilter, \
    BugLinkFilter



#---------------------- Test EquivalenceTranslator -------------------------------
#==========================================================================

def test_EquivalenceTranslator_creation():
    """Create EquivalenceTranslator object"""
    #Test the two legal data formats
    EquivalenceTranslator(
        repos=("Trac",     "Launchpad", "INTERNAL"),
        vals=(("blocker",  "Critical",  "Critical"),
              ("critical", "High",      "High"),
              ("major",    "Medium",    "Medium"),
              ("minor",    "Low",       "Low"),
              ("trivial",  "Wishlist",  "Wishlist"),
              ("trivial",  "Unknown",   "Unknown"),
              ("trivial",  "Undecided", "Undecided")))
    
    EquivalenceTranslator(
        repos=" trac,     launchpad, INTERNAL",
        vals="""blocker,  Critical,  Critical;
                critical, High,      High;
                major,    Medium,    Medium;""")

    #Test the errors -----------
    #Last name in argument repo must be "INTERNAL".
    with pytest.raises(UserFatalError):
        EquivalenceTranslator(
            repos=" trac,     launchpad, some-word-not-INTERNAL",
            vals="""blocker,  Critical,  Critical;
                    critical, High,      High;
                    major,    Medium,    Medium;""")
    
    #There must be at least two columns in the table.
    with pytest.raises(UserFatalError):
        EquivalenceTranslator(
            repos=" INTERNAL",
            vals="""Critical;
                    High;
                    Medium;""")
        
    #All lines must have the same length.
    with pytest.raises(UserFatalError):
        EquivalenceTranslator(
            repos=" trac,     launchpad, INTERNAL",
            vals="""blocker,  Critical,  Critical;
                    critical, High;
                    major,    Medium,    Medium;""")
    
    print "Success!"
    
    
    
def test_EquivalenceTranslator_translation():
    """Test the translation functionality"""
    #Create a translator
    tr = EquivalenceTranslator(
            repos=" trac,      launchpad, INTERNAL",
            vals="""Ali_t,     Ali_l,     Ali;
                    Barbara_t, Barbara_l, Barbara;
                    Klaus_t,   Klaus_l,   Klaus;""")

    #Translate to internal representation
    assert tr.repo2intl("trac", "Ali_t") == "Ali"
    assert tr.repo2intl("trac", "Klaus_t") == "Klaus"
    assert tr.repo2intl("launchpad", "Barbara_l") == "Barbara"
    
    #Translate from internal to repository representation
    assert tr.intl2repo("trac", "Ali") == "Ali_t"
    assert tr.intl2repo("trac", "Klaus") == "Klaus_t"
    assert tr.intl2repo("launchpad", "Barbara") == "Barbara_l"
    
    #Translate from "INTERNAL" to internal - degenerate case so that 
    #algorithms can be more simple
    assert tr.repo2intl("INTERNAL", "Ali") == "Ali"
    assert tr.repo2intl("INTERNAL", "Barbara") == "Barbara"
    assert tr.repo2intl("INTERNAL", "Klaus") == "Klaus"
    
    #Add one new term to the translator, and test it.
    tr.add_table_line(("Dirk_t", "Dirk_l", "Dirk"))
    assert tr.repo2intl("launchpad", "Dirk_l") == "Dirk"
    assert tr.intl2repo("launchpad", "Dirk") == "Dirk_l"
    assert tr.repo2intl("trac", "Dirk_t") == "Dirk"
    assert tr.intl2repo("trac", "Dirk") == "Dirk_t"
    
    #Add identity word, this word is always translated into itself.
    tr.add_identity_word("foo")
    assert tr.repo2intl("launchpad", "foo") == "foo"
    assert tr.intl2repo("launchpad", "foo") == "foo"
    assert tr.repo2intl("trac", "foo") == "foo"
    assert tr.intl2repo("trac", "foo") == "foo"
     
    #Test the two exceptions
    #Unknown repository
    with pytest.raises(UnknownRepoError):
        tr.intl2repo("qwert", "Ali")
    with pytest.raises(UnknownRepoError):
        tr.repo2intl("qwert", "Ali_t")
    #Unknown word
    with pytest.raises(UnknownWordError):
        tr.intl2repo("trac", "Dave")
    with pytest.raises(UnknownWordError):
        tr.repo2intl("trac", "Dave")
        
    print "Success!"



def test_BugLinkTranslator__repo2intl():
    """Test translator for bug link numbers in texts."""
    #TODO: test again ``BugLinkTranslator`` instead of ``BugLinkFilter``.
    #      Resurrect the more detailed tests that were deleted when the test 
    #      was changed to ``BugLinkFilter``.

    #Create helper translator for bug IDs
    tr_id = EquivalenceTranslator(
        repos=" trac,    lp,  INTERNAL",
        vals="""1000,  2000,  0000;
                1001,  2001,  0001;
                1002,  2002,  0002;""")
    #Add line that contains a None
    tr_id.add_table_line(["1003", "2003", None])
    
    #Create the translator for bug links in texts
    trbl = BugLinkTranslator(tr_id)
    
    #Normal use cases 
    print "Known link ------------------"
    #Translate normal link repository: "trac"
    text = "Normal... link bug #1001 is known."
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr.find("bug #0001") != -1
    #Translate normal link repository: "lp"
    text = "Normal... link bug #2001 is known."
    texttr = trbl.repo2intl("lp", text)
    print texttr
    assert texttr.find("bug #0001") != -1
    #Translate normal link, use upper case "Bug", which must be preserved
    text = "Normal... link Bug #1001 is known."
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr.find("Bug #0001") != -1
    #Translate discovery link
    text = 'Discovery link bug #1001@trac is known.'
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr.find("bug #0001") != -1
    #Discovery link: repo name in link is different to ``repo_name`` argument.
    text = 'Discovery link bug #2001@lp is known.'
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr.find("bug #0001") != -1
    
    print "Unknown link ----------------"
    #Translate normal link
    text = "Normal... link bug #1004 is unknown."
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr.find('bug #1004@trac') != -1
    #Translate discovery link
    text = 'Discovery link bug #1004@trac is unknown.'
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr.find('bug #1004@trac') != -1
    #Unknown repository in discovery link: no change
    text = 'Discovery link bug #1004@hello is from unknown repository.'
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr.find('bug #1004@hello') != -1
    #If translator returns the special value ``None``, create discovery link.
    text = "Normal... link bug #1003 translator returns None."
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr.find('bug #1003@trac') != -1    
    
    #errors
    print "Errors ----------------"
    #Must not match on python program code that contains the word bug
    text = """var1 = var2.bug #some comment - must remain unchanged"""
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr == text
    #Links in quotes must remain unchanged
    text = """Quoted links "bug #1001", `bug #1001` - must remain unchanged"""
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr == text
    
    #TODO: test all possible errors
    
    print "finished"



def test_BugLinkTranslator__intl2repo():
    """Test translator for bug link numbers in texts."""
    #Create helper translator for bug IDs
    tr_id = EquivalenceTranslator(
        repos=" trac,    lp,  INTERNAL",
        vals="""1000,  2000,  0000;
                1001,  2001,  0001;
                1002,  2002,  0002;""")
    #Add line that contains a None
    tr_id.add_table_line([None, "2003", "0003"])
    
    #Create the translator for bug links in texts
    trbl = BugLinkTranslator(tr_id)
    
    #Normal use cases 
    print "Known link ------------------"
    #Translate normal link, repository: "trac"
    text = "Normal... link bug #0001 is known."
    texttr = trbl.intl2repo("trac", text)
    print texttr
    assert texttr.find("bug #1001") != -1
    #Translate normal link, repository: "lp"
    text = "Normal... link bug #0001 is known."
    texttr = trbl.intl2repo("lp", text)
    print texttr
    assert texttr.find("bug #2001") != -1
    #Translate normal link, use upper case "Bug", which must be preserved
    text = "Normal... link Bug #0001 is known."
    texttr = trbl.intl2repo("trac", text)
    print texttr
    assert texttr.find("Bug #1001") != -1
    #Discovery links are not translated at all
    text = 'Discovery link bug #1001@trac is not translated.'
    texttr = trbl.intl2repo("trac", text)
    print texttr
    assert texttr.find('bug #1001@trac') != -1
    
    print "Unknown link ----------------"
    #If translator returns the special value ``None``, create discovery link.
    text = "Normal... link bug #0003 is unknown."
    texttr = trbl.intl2repo("trac", text)
    print texttr
    assert texttr.find('bug #0003@INTERNAL') != -1    
    #Translate normal link with unknown ID: all internal bug IDs should be known
    text = "Normal... link bug #0004 is unknown."
    with pytest.raises(UnknownWordError):
        texttr = trbl.intl2repo("trac", text)
        print texttr
    
    #errors
    print "Errors ----------------"
    #Must not match on python program code that contains the word bug
    text = """var1 = var2.bug #some comment - must remain unchanged"""
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr == text
    #Links in quotes must remain unchanged
    text = """Quoted links "bug #1001", `bug #1001` - must remain unchanged"""
    texttr = trbl.repo2intl("trac", text)
    print texttr
    assert texttr == text
    
    print "finished"



def test_BugLinkFilter():
    """Test wrapper object for bug-link translation."""
    #create bug, we'll only use its attribute ``text_long``
    bug0 = BugIntl(None, None, None, None, None, None, None, None, None, None, 
                   None, None, None)
    #Create helper translator for bug IDs
    tr_id = EquivalenceTranslator(
        repos=" trac,    lp,  INTERNAL",
        vals="""1000,  2000,  0000;
                1001,  2001,  0001;
                1002,  2002,  0002;""")
    
    #Create the translator for bug links in texts
    trbl = BugLinkFilter("trac", tr_id)
    
    #Translate normal link from repository format to internal format
    bug = bug0._replace(text_long="Normal... link bug #1001 is known.")
    bugtr = trbl.repo2intl(bug)
    print bugtr.text_long
    assert bugtr.text_long.find("bug #0001") != -1
    #Translate normal link from internal format to repository format
    bug = bug0._replace(text_long="Normal... link bug #0001 is known.")
    bugtr = trbl.intl2repo(bug)
    print bugtr.text_long
    assert bugtr.text_long.find("bug #1001") != -1

    print "finished"



def test_PeopleMilestoneFilter():
    """Test translator for bug link numbers in texts."""
    #create bug, we'll only use its attribute ``text_long``
    bug0 = BugIntl(None, None, None, None, None, None, None, None, None, None, 
                   None, None, None)
    #Create helper translators
    tr_people = EquivalenceTranslator(
        repos=" trac,   lp,  INTERNAL",
        vals="""eike,   ew,  Eike Welk;
                klaus,  km,  Klaus Müller;""")
    tr_milestones = EquivalenceTranslator(
        repos=" trac,          lp,  INTERNAL",
        vals="""0.1-start,  0.1.0,  0.1.0;
                0.2-tryit,  0.2.0,  0.2.0;""")
    
    #Create the translator for bug links in texts
    tr = PeopleMilestoneFilter("trac", tr_people, tr_milestones)
    
    #Create bug with vocabulary from "trac" repository
    bug = bug0._replace(reporter="eike", assigned_to="klaus", 
                        milestone="0.2-tryit")
    
    #convert bug to internal format
    bugint = tr.repo2intl(bug)
    assert bugint.reporter == "Eike Welk"
    assert bugint.assigned_to == "Klaus Müller"
    assert bugint.milestone == "0.2.0"
    
    #convert bug back to "trac" format.
    bugtr = tr.intl2repo(bugint)
    assert bugtr == bug
    assert bugtr != bugint
    
    print "finished"



if __name__ == '__main__':
#    test_EquivalenceTranslator_creation()
#    test_EquivalenceTranslator_translation()
    test_BugLinkTranslator__repo2intl()
    test_BugLinkTranslator__intl2repo()
#    test_BugLinkFilter()
#    test_PeopleMilestoneFilter()
    pass #pylint: disable=W0107
