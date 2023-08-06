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
Common functionality, that is used by all modules.
"""

from __future__ import division
from __future__ import absolute_import              

from collections import namedtuple


#Version of the program
PROGRAM_VERSION = ("0", "1", "0")
PROGRAM_VERSION_STR = ".".join([str(n) for n in PROGRAM_VERSION])

#Descriptions of bug repositories 
#All repository descriptions need a field `repo_name`:

#Trac repository:
TracData = namedtuple("TracData", 
                      "repo_name, url, user_name, password, comment")

#A Project on Launchpad
#No user name or password required; authentication goes through a browser 
#and DBUS.
#TODO: remove attribute authenticate
LaunchpadData = namedtuple("LaunchpadData", 
                           "repo_name, project_name, cachedir, comment")

#A repository that does nothing.
DummyRepoData = namedtuple("DummyRepoData", "repo_name, initial_bugs")

#A task to synchronize several repositories.
SyncTaskData = namedtuple("SyncTaskData", 
                          "task_name, repos_list, "
                          "people_translator, milestone_translator, ")

"""
Description of a bug

-------------------------------------------
Bug states (similar to Trac)

-------------------------------------------
status      priority resolution kind       
----------- -------- ---------- -----------
new         blocker  fixed      defect     
confirmed   critical invalid    enhancement
in_progress major    wontfix    task       
closed      minor    duplicate  *         
*           trivial  worksforme            
            *        none                 
                     *                    
-------------------------------------------
Star "*" means unknown, take value from other bug.
""" #IGNORE:W0105
#TODO: Work out how IDs are used. Currently ``ids`` has two functions:
#      * It is used like a tuple (repo_where_bug_came_from, ID_in_this_repo), 
#        for bugs that were received from the repositories.
#      * It is used like a dict (repo_name, bug_ID_in_this_repo) when bug is
#        stored as known bug, and to build the ID translator when a SyncTask 
#        is created.
#
#      * The bug's mutable ``ids`` attribute makes deepcopy necessary everywhere!
#
#      * Ideas for bug's ID related attributes:
#        * Two immutable attributes: bug.repo, bug.id: 
#          * Good representation only for reading bugs.
#          * For updating bugs the bug IDs have to be given separately.
#          * Giving bug ID separately makes tests more easy. Current code::
#                bug0g = repo.get_bugs([id0])
#                bug0m = bug0g._replace(text_short="New title for bug 0")
#                repo.update_bugs([bug0m])
#            Future code::
#                bug0m = bug0._replace(text_short="New title for bug 0")
#                repo.update_bugs([bug0m],[id0])
#
#          * The translation table has to be stored separately. Or:
#          * Known bugs could be stored in a small tree:
#            namedtuple("KnownBug", "bug:BugData, ids:dict[(str,str)]")
#
#        * Bug IDs should be random integer strings (6 digits)        
#              The new bug IDs could be permanent, and therefore embedded 
#              in "magic" text in the bug description. This would give easy 
#              backup capabilities for the database of bug associations.
#
#        * The merging algorithm could return a complete bug, potentially 
#          with a new ID.
#        * The writing algorithm would use separate data structures to 
#          store newly discovered bug IDs. New bug IDs are received from 
#          repositories when bugs are created.
BugData = namedtuple("BugData", 
                     "ids, "                                #administrative
                     "time_created, time_modified, "   
                     "text_short, text_long, "              #text
                     "reporter, assigned_to, "              #people
                     "status, priority, resolution, kind,"  #bug life cycle
                     "milestone,")                          #grouping

#Task to merge bug fields or to create a new bug.
#TODO: rename: internal_bug -> known_bug
BugMergeTask = namedtuple("BugMergeTask", "internal_bug, repo_bugs")

"""
Structure to control uploading of a single bug to the bug repositories.

Attributes
----------
bug: BugData
    The bug that is uploaded to the repositories.
     
create_in, update_in: list[str]
    List of repositories (names) where bug will be created/updated.
    
add_internal: bool
    Create new internal bug if none exists, if True.
""" #IGNORE:W0105
BugWriteTask = namedtuple("BugWriteTask", 
                          "bug, create_in, update_in, add_internal")


class UserFatalError(Exception):
    """
    A fatal error, for which the user is responsible (not the programmer).
    
    This exception does not signify a bug.
    When it is raised, the program is terminated, and its error 
    message is presented to the user.
    """
    pass

class UnknownRepoError(KeyError):
    """
    An EquivalenceTranslator is asked to translate to/from a repository it 
    does not know.
    """
    pass

class UnknownWordError(KeyError):
    """
    An EquivalenceTranslator is asked to translate a word it does not know.
    """
    pass


class EquivalenceTranslatorBase(object):
    """Base class of translators that can be expressed as a 2D table."""
    #pylint: disable=W0613
    def add_table_line(self, line):
        """Add translation of term to translator.""" 
        raise NotImplementedError()
    
    def intl2repo(self, repo_name, word):
        """Translate: internal -> repository."""
        raise NotImplementedError()
    
    def repo2intl(self, repo_name, word):
        """Translate: repository -> internal."""
        raise NotImplementedError()
    
    def add_identity_word(self, word):
        """Add word that is translated into itself in all directions."""
        raise NotImplementedError()
    
    
    


class EquivalenceTranslatorNoop(EquivalenceTranslatorBase):
    """EquivalenceTranslator that does nothing. Useful for debugging."""
    #pylint: disable=W0613
    def add_table_line(self, line):
        """Add translation of term to translator: raises exception.""" 
        raise Exception("This translator does not translate at all!")
    
    def intl2repo(self, repo_name, word):
        """Translate: internal -> repository: Returns word unchanged."""
        return word
    
    def repo2intl(self, repo_name, word):
        """Translate: repository -> internal: Returns word unchanged."""
        return word
    
    def add_identity_word(self, word):
        """Add word that is translated into itself in all directions."""
        return None



class EquivalenceTranslator(EquivalenceTranslatorBase):
    """
    Translate a bug attribute from its representations in a bug 
    repository, to an internal representation and back. It assumes that 
    there are equivalent terms for this attribute on all trackers.
    
    This translator works well for people and bug IDs. It does not work very well
    for bug status fields, because different trackers have different models and 
    workflows. 
    
    A table describes the translations that should be made. Each row in the 
    table contains terms that are equivalent, and should be translated into 
    each other. The columns represent the vocabulary of a specific tracker. 
    
        EquivalenceTranslator(
            repos=("Trac",     "Launchpad", "INTERNAL"),
            vals=(("blocker",  "Critical",  "Critical"),
                  ("critical", "High",      "High"),
                  ("major",    "Medium",    "Medium"),
                  ("minor",    "Low",       "Low")))
                        
    Alternatively strings can be used, commas (,) separate columns, 
    semicolons (;) separate rows:
    
        EquivalenceTranslator(
            repos=" trac,     launchpad, INTERNAL",
            vals='''blocker,  Critical,  Critical;
                    critical, High,      High;
                    major,    Medium,    Medium;
                    minor,    Low,       Low''')
    
    Lines can be added to the translation table at any time with the
    method `add_table_line`.
    """
    def __init__(self, repos, vals):
        assert isinstance(repos, (str, tuple, list))
        assert isinstance(vals, (str, tuple, list))
        EquivalenceTranslatorBase.__init__(self)
        
        #Test argument `repos`
        #Convert comma separated strings into list of strings.
        if isinstance(repos, str):
            repos = [s.strip() for s in repos.split(",")]
        #Test: last element must be string "INTERNAL".
        if repos[-1] != "INTERNAL":
            raise UserFatalError("Argument `repos`: "
                                 "Last element must be string 'INTERNAL', "
                                 "but  it is: {r}".format(r=repos[-1]))
        #Test: There must be at least two columns in the table 
        #      (otherwise there is nothing to translate).
        if len(repos) < 2:
            raise UserFatalError("Argument `repos`: "
                                 "There must be at least two elements.")
        self.repo_names = repos
        
        #Test argument `vals`
        #Convert 2D CSV table into nested lists
        if isinstance(vals, str):
            #Remove optional trailing ";"
            vals = vals.strip()
            if vals and vals[-1] == ";":
                vals = vals[:-1]
            #Split into rows that are separated by ";"
            rows = vals.split(";")
            #Split each row into words that are separated by ","
            vals_raw = [row.split(",") for row in rows]
            #Remove leading and trailing whitespace around each word.
            vals = [[word.strip() for word in row] for row in vals_raw]
        #All lines must have the same length.
        for line in vals:
            if len(line) != len(repos):
                raise UserFatalError("Argument `vals`: "
                                     "All lines must have the same length, and "
                                     "the same length as argument `repos`.")
        
        #Build translation dicts, and the table `self.vals`.
        self.vals = []
        #dictionaries of dictionaries, the name of the repository is the key 
        #The inner dictionaries translate between the repo's vocabularies and 
        #the internal vocabulary. 
        self.repo_to_internal_dict = {}
        self.internal_to_repo_dict = {}
        for repo_name in self.repo_names[:-1]:
            self.repo_to_internal_dict[repo_name] = {}
            self.internal_to_repo_dict[repo_name] = {}
        for line in vals:
            self.add_table_line(line)
        

    def add_table_line(self, line):
        """
        Add the translation of one term to the translator. 
        Builds the translation dictionaries and the table `self.vals`.
        
        Argument `line`:tuple is one line of the table `self.vals`
        """ 
        assert len(line) == len(self.repo_names)
        
        #Add line to the table
        self.vals.append(line)
        #Add translations to the dictionaries
        for i, repo_name in enumerate(self.repo_names[:-1]):
            self.repo_to_internal_dict[repo_name][line[i]] = line[-1]
            self.internal_to_repo_dict[repo_name][line[-1]] = line[i]
    
    
    def intl2repo(self, repo_name, word):
        """
        Translate: internal -> repository
        
        Translate a word from the internal representation to the representation
        of a specific repository.
        """
        try:
            trans_dict = self.internal_to_repo_dict[repo_name]
        except KeyError:
            raise UnknownRepoError(repo_name)
        
        try:
            return trans_dict[word]
        except KeyError:
            raise UnknownWordError(word) 
        
    
    def repo2intl(self, repo_name, word):
        """
        Translate: repository -> internal 
        
        Translate a word from the representation of a specific repository the 
        internal representation.
        
        Arguments
        ---------
        repo_name
            Name of a repository. ``word`` is translated from the vocabulary 
            of this repository to the internal vocabulary.
            
            Degenerate case: If ``repo_name == "INTERNAL"`` then ``word`` 
            is simply returned untranslated.
            
        word
            The word that is translated to the internal vocabulary.
        
        Returns
        -------
        Translation of ``word`` to the internal vocabulary.
        """
        #Handle degenerate case "INTERNAL" -> internal 
        if repo_name == "INTERNAL":
            if word not in self.internal_to_repo_dict.values()[0]:
                raise UnknownWordError(word) 
            return word
        
        try:
            trans_dict = self.repo_to_internal_dict[repo_name]
        except KeyError:
            raise UnknownRepoError(repo_name)
        
        try:
            return trans_dict[word]
        except KeyError:
            raise UnknownWordError(word) 

    
    def add_identity_word(self, word):
        """Add word that is always translated into itself."""
        #TODO: This feature is unused. Remove?
        line = [word] * len(self.repo_names)
        self.add_table_line(line)
    
    
