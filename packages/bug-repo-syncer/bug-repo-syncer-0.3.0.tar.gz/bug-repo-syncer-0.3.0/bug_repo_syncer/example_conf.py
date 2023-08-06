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

#TODO: GPL exception for the file, if it is copied to a user's project 
#      directory.

#@@@[[[------------------------- Cut here! ------------------------------------
# -*- coding: utf-8 -*-
"""
Example configuration for Bug Repo Syncer

This is the configuration for the test repositories of Bug Repo Syncer. 

The **test** repositories are:
    https://qastaging.launchpad.net/bug-repo-syncer    (server="qastaging")
    https://staging.launchpad.net/bug-repo-syncer      (server="staging")
    http://sourceforge.net/apps/trac/repo-syncer-tst 

The **real** bug repositories are:
    https://bugs.launchpad.net/bug-repo-syncer         (server="production")
    http://sourceforge.net/apps/trac/bug-repo-syncer


WARNING
-------

This configuration file is an executable piece of software in the Python 
programming language. It is loaded as a Python module (library) by the
``bsync`` program, shortly after the start of the program. The instructions in 
this file are executed once when it is loaded. 

You could put any code here, even code that deletes your home directory. Don't 
take a configuration file for Bug Repo Syncer from someone you don't trust!
"""

from __future__ import division
from __future__ import absolute_import              

from bug_repo_syncer.common import (TracData, LaunchpadData, SyncTaskData, 
                               EquivalenceTranslator)


#    *** This object is accessed by the program! ***
#Version of the configuration file format - for future changes of file format.
FORMAT_VERSION = "0.2"

#Describe the bug repositories 
#Launchpad: 
#    The authentication for Launchpad goes through a browser and DBUS. 
#    Therefore user name and password are not required here. When you start 
#    the program for the first time, you will be asked for user name and 
#    password in a browser window.
#
#    repo_name: 
#        Nickname of repository, can be any string, will be used for this  
#        repository everywhere in the program, also in stored data.
#    project_name:
#        Real name of project on Launchpad, bugs of this project are 
#        synchronized.
#    cachedir:
#        Path to writable directory, used only for anonymous login.
#        If `cachedir=None`, program chooses directory automatically. 
#        Currently: `~/.launchpadlib`
#    server:
#        Name of the server instance, Launchpad calls them service roots. 
#        There are several such instances, the most important are: 
#            * "production": the real Launchpad server.
#            * "qastaging": a special server for tests. The data on this server
#              is erased every few weeks and replace by the contents of 
#              "production".
#            * "staging": An other test server for launchpad. If "qastaging"
#              is too slow use "staging", and vice versa.
#        In principle you could put the URL of your private Launchpad server 
#        there.
#    comment: 
#        Any text
lp_data = LaunchpadData(repo_name="lp", project_name="bug-repo-syncer",
                        cachedir=None, server="staging",
                        comment="Test repository for 'bug-repo-syncer' on "
                                "Launchpad")
#Trac:
#    repo_name: 
#        Nickname of repository, can be any string, will be used for this  
#        repository everywhere in the program, also in stored data.
#    url:
#        Root URL of Trac repository. The URL of Bug Repo Syncer's real bug 
#        repository is:
#            http://sourceforge.net/apps/trac/bug-repo-syncer/
#    user_name: 
#        Your user name for the Trac repository.
#    password: 
#        Your real password for the Trac site. If ``password=None`` the program
#        asks for the password when it wants to log into the server. For 
#        anonymous login the password is ignored.
#    comment: 
#        Any text    
trac_data = TracData(repo_name="trac", 
                     url="http://sourceforge.net/apps/trac/repo-syncer-tst",           
                     user_name="eike", password=None,
                     comment="Test Trac repository for 'bug-repo-syncer' on "
                             "Sourceforge")


#Translate the names of people and milestones from one repository to the other.
#    repos:
#        String that contains list of repository names. These must be the 
#        exact names (`repo_name`) from the repository descriptions above.
#        The last name must be the string ``INTERNAL``. It labels the words 
#        that are used internally, and in the stored data.
#    vals:
#        Table of words that should be translated. Columns are separated by 
#        commas (``,``), lines must end with a semicolon (``;``).
#Equivalent user names in the repositories.
people = EquivalenceTranslator(
            repos=" trac,     lp,         INTERNAL",
            vals="""eike,     eike-welk,  Eike Welk;""")

#Equivalent milestone names.
milestones = EquivalenceTranslator(
            repos=" trac,     lp,         INTERNAL",
            vals="""0.0.1,    0.0.1,      0.0.1;   
                    0.1.0,    0.1.0,      0.1.0;   
                    0.2.0,    0.2.0,      0.2.0;  """)


#    *** This object is accessed by the program! ***
#Put everything from above into one object:
#A task to synchronize several repositories.
#    task_name:
#        Any string, currently only displayed by the ``info`` command.
#    repos_list:
#        List of repository descriptions. 
#    people_translator: 
#        Object that translates the names of people between repositories.
#    milestone_translator:
#        Object that translates the names of milestones between repositories.
#    add_unknown_milestones: True/False
#        If True: Add unknown milestones to the milestone translator. The new
#        name is added to all repositories identically. 
#        If False: Unknown milestones are translated to the string "*".
#        
#        This feature does not add milestones to the repositories. It will
#        nevertheless make new milestones appear in Trac repositories 
#        automatically. Milestones only have to be put into the milestone 
#        translator explicitly, when you use different names for them in your 
#        repositories. 
#    translate_bug_links: True/False
#        If True: Translate bug IDs that appear in certain patterns 
#        ("bug #123") in the text sections. The web front ends (of Trac and
#        Launchpad at least) display these patterns as links to the specified
#        bugs. The bug IDs stay valid, when the text is uploaded to an other
#        repository.  
#        If False: Don't change bug IDs.
repo_config = SyncTaskData(task_name="bug-repo-syncer", 
                           repos_list=[lp_data, trac_data], 
                           people_translator=people, 
                           milestone_translator=milestones,
                           add_unknown_milestones=True,
                           translate_bug_links=True)

"""
Bug states in different bug repositories
======================================================================================================

-------------------------------------------
Internal (similar to Trac)
-------------------------------------------
Status      Priority Resolution Kind       
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


----------------------------------------------------------------------------------------------------
Launchpad                  Trac                                       Bitbucket                     
------------------------   ----------------------------------------   ------------------------------
Status        Importance   Status   Priority Resolution Type          status    priority kind       
------------- ----------   -------- -------- ---------- -----------   --------- -------- -----------
New           Unknown      new      blocker  fixed      defect        new       blocker  bug        
Incomplete    Critical     assigned critical invalid    enhancement   open      critical enhancement
Opinion       High         accepted major    wontfix    task          resolved  major    proposal   
Invalid       Medium       closed   minor    duplicate                invalid   minor    task       
Won't Fix     Low          reopened trivial  worksforme               duplicate trivial             
Expired       Wishlist                       None                     wontfix                       
Confirmed     Undecided                                               on hold                       
Triaged                                                                                             
In Progress                                                                                         
Fix Committed                                                                                       
Fix Released                                                                                        
Unknown                                                                                             
----------------------------------------------------------------------------------------------------
""" #pylint: disable=W0105
