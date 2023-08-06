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

from bug_syncer.common import UserFatalError, UnknownRepoError, \
    UnknownWordError, EquivalenceTranslator



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
        
    #There must be at least one line in the table
    with pytest.raises(UserFatalError):
        EquivalenceTranslator(
            repos=" trac, launchpad, INTERNAL",
            vals=" ")
        
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



if __name__ == '__main__':
    test_EquivalenceTranslator_creation()
    test_EquivalenceTranslator_translation()
    pass #pylint: disable=W0107