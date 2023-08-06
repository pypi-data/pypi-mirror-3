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

import re
from collections import namedtuple



#Version of the program
PROGRAM_VERSION = ("0", "3", "0")
PROGRAM_VERSION_STR = ".".join(PROGRAM_VERSION)

#Version of configuration file format
CONF_FORMAT_VERSION = "0.2"

#Descriptions of bug repositories 
#All repository descriptions need a field `repo_name`:

#Trac repository:
TracData = namedtuple("TracData", 
                      "repo_name, url, user_name, password, comment")

#A Project on Launchpad
#No user name or password required; authentication goes through a browser 
#and DBUS.
LaunchpadData = namedtuple("LaunchpadData", 
                           "repo_name, project_name, cachedir, server, comment")

#A repository that does nothing.
DummyRepoData = namedtuple("DummyRepoData", "repo_name, initial_bugs")

#A task to synchronize several repositories.
SyncTaskData = namedtuple("SyncTaskData", 
                          "task_name, repos_list, "
                          "people_translator, milestone_translator, "
                          "add_unknown_milestones, translate_bug_links")

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
State "*" means undecided, take the information from an other repository. 
This way you can have "major" "enhancement" in Trac, while it is just 
"Wishlist" in Launchpad.
""" #IGNORE:W0105
BugIntlBase = namedtuple(
                         "BugIntlBase", 
                         "repo_name, id, "                      #administrative
                         "time_created, time_modified, "   
                         "text_short, text_long, "              #text
                         "reporter, assigned_to, "              #people
                         "status, priority, resolution, kind,"  #bug life cycle
                         "milestone,")                          #grouping
class BugIntl(BugIntlBase):  #IGNORE:W0232
    def fancy_str(self):
        """Convert to a good looking string"""
        try:
            #pylint: disable=E1101
            outs = u""
            outs += "Modified:  " + str(self.time_modified)
            outs += "  Created: " + str(self.time_created) + "\n"
            outs += "Reporter:  {r:20}".format(r=self.reporter)
            outs += " Assignee: " + str(self.assigned_to) + "\n"
            outs += "Milestone: " + str(self.milestone) + "\n"
            outs += "{stat:10} {kind:10} {prio:10} {res:10} \n" \
                    .format(stat=self.status, kind=self.kind, 
                            prio=self.priority, res=self.resolution)
            outs += "Repository:{r:20} ID: {i} \n\n" \
                    .format(r=self.repo_name, i=self.id)
            outs += self.text_short + "\n"
            outs += "\n" + self.text_long + "\n"
            outs += "--------------------------------------------------------\n"
            return outs.encode("utf8", errors="replace")
        except AttributeError, e:
            print "Warning: BugIntl: ", str(e)
            return BugIntlBase.__str__(self)
    

BUG_CONTENTS_FIELDS = list(set(BugIntl._fields).difference( #IGNORE:E1101
                        ["repo_name", "id", "time_created", "time_modified"]))
def equal_contents(bug1, bug2):
    """ 
    Test if bugs are equal, but ignore fields that the repositories 
    always change. 
    """
    for fname in BUG_CONTENTS_FIELDS:
        if getattr(bug1, fname) != getattr(bug2, fname):
            return False
    return True


        
#The data that the application knows about a bug: 
#its IDs in the different repositories, and the contents of the bug itself
KnownBugData = namedtuple("KnownBugData", "ids, bug")
        
#Task to merge bug fields or to create a new bug.
BugMergeTask = namedtuple("BugMergeTask", 
                          "internal_bug, repo_bugs, internal_id, create_intl")


"""
Structure to control uploading of a single bug to the bug repositories.

Attributes
----------
bug: BugIntl
    The bug that is uploaded to the repositories.
     
internal_id: str
    Internal ID of this bug.
    
create_intl: bool
    Create new internal bug, if True.
""" #IGNORE:W0105
BaseBugWriteTask = namedtuple("BugWriteTask", 
                              "ids, bug, internal_id, create_intl")
class BugWriteTask(BaseBugWriteTask): #IGNORE:W0232
    def fancy_str(self):
        """Convert to a good looking string."""
        try:
            #pylint: disable=E1101
            outs = u""
            outs += "IDs: " + str(self.ids) + "\n"
            outs += self.bug.fancy_str().decode("utf8", errors="replace") 
            return outs.encode("utf8", errors="replace")
        except AttributeError, e:
            print "Warning: BugWriteTask: ", str(e)
            return BaseBugWriteTask.__str__(self)



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
    def add_table_line(self, line):
        """Add translation of term to link_trans.""" 
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
    def add_table_line(self, line):
        """Add translation of term to link_trans: raises exception.""" 
        raise Exception("This link_trans does not translate at all!")
    
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
    
    This link_trans works well for people and bug IDs. It does not work very well
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
            rows = vals.split(";") if vals else []
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
        Add the translation of one term to the link_trans. 
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
        line = [word] * len(self.repo_names)
        self.add_table_line(line)
    
    

class BugLinkTranslator(object):
    """
    Translate bug links in strings.
    
    Bug IDs that appear in certain patterns are translated, so that the bug IDs
    stay valid when the text (as part of a bug) is uploaded to an other 
    repository.
    
    Two pattern are supported:
    
    "bug #123" : The normal format.
        This pattern is converted to (HTML) links in the web front ends of all
        repositories.
        
    "bug #123@repo" : The discovery format.
        Used if the bug ID is unknown to bug-repo-syncer. The bug IDs will 
        usually become known later, for example after bugs have been created 
        in a the repository. As bug-repo-syncer usually looks at all changed 
        bugs for a second time, these discovery links are quickly exchanged by
        normal links.  
    """
    def __init__(self, id_translator=EquivalenceTranslatorNoop()):
        """
        Arguments
        ---------
        id_trans: EquivalenceTranslatorBase
            Object to translate bug IDs from one repository to an other.
        """
        assert isinstance(id_translator, EquivalenceTranslatorBase)
        #Translates bug IDs between different repositories
        self.id_trans = id_translator
        #Template for a normal bug link: "bug #123" 
        self.normal_tmpl = u"{kwd} #{id}"
        #Template for a discovery bug link: "bug #123@repo"
        self.discovery_tmpl = u"{kwd} #{id}@{repo}"
        
        #Regular expression to recognize "normal" and "discovery" bug links.
        #The two types of bug links look like this:
        # * Normal bug link: "bug #123" 
        # * Discovery bug link: "bug #123@repo"
        #
        #The regular expression has three named groups:
        #    "kwd:   keyword, for example: "bug", "Bug", "BUG"
        #    "id":   the bug ID, "123" in the example.
        #    "repo": repository name. ``None`` if link is normal link.
        #
        all_re = """(?<![^\s\(])          #must be preceded by one of " (" 
                    (?P<kwd>bug)          #text "bug" 
                    \ \#                  #single space + "#"
                    (?P<id>\w\d*)         #for example "a123"
                    (@                    #char "@"; start of optional group
                    (?P<repo>[\w-]+))?    #word of alphanumeric, "-" 
                    (?![^\s\)\.,;])       #must be followed by one of " ).,;"
                 """
        self.all_re = re.compile(all_re, re.I | re.U | re.X) # | re.DEBUG)
        
        
    def intl2repo(self, repo_name, text):
        """Translate: internal -> repository."""
        def translate_link(match):
            """Translate one bug link from internal format to repo format."""
            keyword = match.group("kwd")
            org_id = match.group("id")
            repo = match.group("repo")
            if repo is not None:
                #Discovery format: "bug #123@foo"
                #Don't translate discovery format if direction is: intl -> repo
                #Really necessary would be: repo1 -> intl -> repo2 in this case.
                #And it is pointless, we currently don't know these bug IDs.
                #Return all matched text.
                return match.group(0)
            
            #normal format: "bug #123"
            tra_id = self.id_trans.intl2repo(repo_name, org_id)
            if tra_id is None:
                #The translator can't translate the ID, create a discovery link
                link = self.discovery_tmpl.format(
                                    kwd=keyword, id=org_id, repo="INTERNAL")
            else:
                #Regular case: create translated normal bug-link
                link = self.normal_tmpl.format(kwd=keyword, id=tra_id)
            return link
        
        #Substitute the links with translated versions
        tra_text = self.all_re.sub(translate_link, text)
        return tra_text
         
        
    def repo2intl(self, repo_name, text):
        """Translate: repository -> internal."""
        def translate_link(match):
            """Translate one bug link from repo format to internal format."""
            keyword = match.group("kwd")
            org_id = match.group("id")
            link_repo = match.group("repo")
            #For normal format ("bug #123") use supplied repository name
            if link_repo is None:
                link_repo = repo_name
            
            #Translate the bug
            try:
                #Create normal link
                tra_id = self.id_trans.repo2intl(link_repo, org_id)
                if tra_id is None:
                    raise UnknownWordError
                link = self.normal_tmpl.format(kwd=keyword, id=tra_id)
            except (UnknownWordError, UnknownRepoError):
                #If anything was unknown, create discovery link
                link = self.discovery_tmpl.format(
                                    kwd=keyword, id=org_id, repo=link_repo)
            return link
        
        #Substitute the links with translated versions
        tra_text = self.all_re.sub(translate_link, text)
        return tra_text



class FilterBase(object):
    """
    Base class for filters, objects that convert (translate) a certain 
    aspect of a bug. Filters get a bug as their input, and return a 
    converted bug.
    """
    def intl2repo(self, bug):
        """Translate: internal -> repository."""
        raise NotImplementedError()
    
    def repo2intl(self, bug):
        """Translate: repository -> internal."""
        raise NotImplementedError()
    

    
class FilterNoop(FilterBase):
    """Filter that does nothing. For test code."""
    def __init__(self):
        FilterBase.__init__(self)
        
    def intl2repo(self, bug):
        """Translate: internal -> repository."""
        return bug
    
    def repo2intl(self, bug):
        """Translate: repository -> internal."""
        return bug



class BugLinkFilter(FilterBase):
    """Translate bug links in the ``text_long`` attribute of a bug."""
    def __init__(self, repo_name, 
                 id_trans=EquivalenceTranslatorNoop(),
                 only_intl2repo=False):
        """ 
        Arguments
        ---------
        repo_name: str
            name of the repository for which the link translator works.
        
        id_trans: EquivalenceTranslatorBase
            Object to translate bug IDs from internal format to repository 
            format and vice versa. 
            
        only_intl2repo: bool
            If True: translate only in ``intl2repo``, ``repo2intl`` returns the 
            bug unchanged. Both methods (``intl2repo`` and ``repo2intl``) 
            translate bug-links otherwise.
        """
        FilterBase.__init__(self)
        assert isinstance(repo_name, (str, unicode))
        assert isinstance(id_trans, EquivalenceTranslatorBase)
        assert isinstance(only_intl2repo, bool)
        
        self.repo_name = repo_name
        self.id_trans = id_trans
        self.link_trans = BugLinkTranslator(id_trans)
        self.only_intl2repo = only_intl2repo
        
        
    def intl2repo(self, bug):
        """Translate: internal -> repository."""
        tra_text = self.link_trans.intl2repo(self.repo_name, bug.text_long)
        tra_bug = bug._replace(text_long=tra_text)
        return tra_bug
         
        
    def repo2intl(self, bug):
        """Translate: repository -> internal."""
        if self.only_intl2repo:
            return bug
        
        tra_text = self.link_trans.repo2intl(self.repo_name, bug.text_long)
        tra_bug = bug._replace(text_long=tra_text)
        return tra_bug



class PeopleMilestoneFilter(FilterBase):
    """
    Translate people and milestones in bugs.
    """
    #TODO: good documentation
    def __init__(self, repo_name, 
                 people_translator=EquivalenceTranslatorNoop(), 
                 milestone_translator=EquivalenceTranslatorNoop(), 
                 add_unknown_milestones=True):
        """
        Arguments
        ---------
        repo_name: str
            Name of the repository for which bugs are translated. 
            Needed to identify the repository at ``people_translator`` 
            and ``milestone_translator``.
        
        people_translator: EquivalenceTranslatorBase
            Translates people's names between the repositories.
        
        milestone_translator: EquivalenceTranslatorBase
            Translates names of milestones between the repositories.
        
        add_unknown_milestones: bool
            Add unknown milestones to the milestone link_trans. The new name is 
            added to all repositories identically.
        """
        assert isinstance(repo_name, (str, unicode))
        assert isinstance(people_translator, EquivalenceTranslatorBase)
        assert isinstance(milestone_translator, EquivalenceTranslatorBase)
        assert isinstance(add_unknown_milestones, bool)
        FilterBase.__init__(self)
        #Name of the repository. Used as key everywhere
        self.repo_name = repo_name
        #Translate people and milestone names between repositories
        #types EquivalenceTranslatorNoop, EquivalenceTranslator
        self.people_translator = people_translator
        self.milestone_translator = milestone_translator
        #If True: add unknown milestones to milestone link_trans, see
        # ``self.milestone_repo2intl`` for details
        self.add_unknown_milestones = add_unknown_milestones

    def intl2repo(self, bug):
        """Translate: internal -> repository."""
        reporter = self.people_intl2repo(bug.reporter)
        assigned = self.people_intl2repo(bug.assigned_to)
        milestone = self.milestone_intl2repo(bug.milestone)
        tra_bug = bug._replace(reporter=reporter, assigned_to=assigned, 
                               milestone=milestone)
        return tra_bug
    
    def repo2intl(self, bug):
        """Translate: repository -> internal."""
        reporter = self.people_repo2intl(bug.reporter)
        assigned = self.people_repo2intl(bug.assigned_to)
        milestone = self.milestone_repo2intl(bug.milestone)
        tra_bug = bug._replace(reporter=reporter, assigned_to=assigned, 
                               milestone=milestone)
        return tra_bug
    
    def people_intl2repo(self, name):
        """
        Translate name of people from internal to repository vocabulary.
        """
        if self.people_translator is None:
            return name
        elif name is None or name == "*":
            return name
        else:
            return self.people_translator.intl2repo(self.repo_name, name)
    
    def people_repo2intl(self, name):
        """
        Translate name of people from repository to internal vocabulary.
        """
        if self.people_translator is None:
            return name
        elif name is None:
            return None
        try:
            return self.people_translator.repo2intl(self.repo_name, name)
        except UnknownWordError:
            print "Warning! Unknown person: '{p}'".format(p=name)
            return "*"
    
    def milestone_intl2repo(self, ms_name):
        """
        Translate name of milestone from internal to repository vocabulary.
        """
        if self.milestone_translator is None:
            return ms_name
        elif ms_name is None or ms_name == "*":
            return ms_name
        else:
            return self.milestone_translator.intl2repo(self.repo_name, ms_name)
    
    def milestone_repo2intl(self, ms_name):
        """
        Translate name of milestone from repository to internal vocabulary.
        
        None
        ----
        If ``ms_name == None`` then None is returned. Otherwise the word is 
        translated.
        
        Unknown Milestones:
        -------------------
        If ``self.add_unknown_milestones == True`` then unknown milestone names 
        are added as identical words to all repositories. Otherwise unknown
        milestones are converted to the string "*". 
        """
        if self.milestone_translator is None:
            return ms_name
        elif ms_name is None:
            return None
        try:
            return self.milestone_translator.repo2intl(self.repo_name, ms_name)
        except UnknownWordError:
            if self.add_unknown_milestones:
                print "Adding unknown milestone: '{m}' to link_trans" \
                      .format(m=ms_name)
                self.milestone_translator.add_identity_word(ms_name)
                return ms_name
            else:
                print "Warning! Unknown milestone: '{m}'".format(m=ms_name)
                return "*"


