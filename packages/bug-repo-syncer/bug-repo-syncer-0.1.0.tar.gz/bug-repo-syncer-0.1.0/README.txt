.. ############################################################################
   #   Bug Repo Syncer - A program to synchronize bug repositories.           #
   #                                                                          #
   #   Copyright (C) 2012 by Eike Welk                                        #
   #   eike.welk@gmx.net                                                      #
   #                                                                          #
   #   License: GPL V3                                                        #
   #                                                                          #
   #   This program is free software: you can redistribute it and/or modify   #
   #   it under the terms of the GNU General Public License as published by   #
   #   the Free Software Foundation, either version 3 of the License, or      #
   #   (at your option) any later version.                                    #
   #                                                                          #
   #   This program is distributed in the hope that it will be useful,        #
   #   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
   #   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
   #   GNU General Public License for more details.                           #
   #                                                                          #
   #   You should have received a copy of the GNU General Public License      #
   #   along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
   ############################################################################

..  This text contains reStructuredText markup. You can convert it to HTML with
    the following command::

        rst2html.py README.txt README.html

===============================================================================
                               Bug Repo Syncer
===============================================================================

*Bug Repo Syncer* is a command line program to synchronize bug repositories. It
currently works with Launchpad and Trac. It can in principle also be used to
migrate between these repositories. The main motivation to write this program,
is the lack of a Mylyn connector for Launchpad, while there exists a Mylyn
connector for Trac.

The program synchronizes its own bug trackers: the project's bugs on Launchpad
with a Trac site on Sourceforge. 

https://bugs.launchpad.net/bug-repo-syncer

http://sourceforge.net/apps/trac/bug-repo-syncer/report/6

*Bug Repo Syncer* is licensed under the GNU General Public License (GPL) 
Version 3.


Deficiencies
===============================================================================

The program is currently incomplete. Also the approach to translate between
repositories with significantly different concepts, has inherent drawbacks.

* *Bug Repo Syncer* does not synchronize bug comments.

* Bug status values (status, priority, resolution, type) can only be roughly
  translated between repositories of different type. *Bug Repo Syncer* uses
  internally a fairly simple model, that is quite similar to the way how Trac
  works. When *Bug Repo Syncer* changes a bug, the status values are set in
  accordance with this simple model. This way information is lost, especially
  from Launchpad's fairly fine grained model.


Dependencies
===============================================================================

The program is developed on Linux. It uses however nothing Linux specific,
and may therefore work on other Unix-like operating systems such as Mac OS X. 

The following software is required to run *Bug Repo Syncer*:

**Python**
    An installation of the Python programming language.

**diff3**
    A command line program to merge text. Present on nearly all Linux and Unix
    installations.

**Dateutil**
    A Python library to process dates. Usually installed on Linux by default.
    
**Launchpadlib**
    A library to access launchpad from Python programs.
    Install it with:: 

        pip install launchpadlib


Installation
===============================================================================

Open a shell window and type::

    pip install bug-repo-syncer

Alternatively download the source archive, extract it, change into the
extracted directory, and type the familiar::

    python setup.py install


Operation
===============================================================================

*Bug Repo Syncer* has the notion of a *project directory*, where configuration
and data files are stored. For normal operation it is assumed that the user 
changes into the project directory and types the synchronization command(s).

Synchronization commands are executed with the ``bsync`` program, it uses
sub-commands like Bazaar's ``bzr`` program.

General Options
---------------

The general options precede the sub-commands. For example, synchronize and
specify the project directory explicitly::

    bsync --project-dir path/to/project/dir sync

-h, --help            
    Show a help message and exit.

--project-dir DIRECTORY
    Specify the directory with configuration and data files.

(Sub-) Commands
---------------

All sub-commands have their own option ``--help``, that shows a specific help
message. To get the help message for the sub-command ``sync`` for example, type::

    bsync sync --help

``init``
........

Create a configuration file in the current directory. The generated
configuration file must be edited, so that it refers to your bug repositories.
To invoke the sub-command type::

    bsync init

``info``                
........

Show status of project directory. ::

    bsync info


``sync``                
........

Synchronize the repositories. ::

    bsync sync

This sub-command has further options:

--since DATE_TIME  
    Consider changes since this date (and time).


Bug Reports and Hacking 
===============================================================================

Bugs reports should be filed in the project's bug tracker on Launchpad. They
can in principle also be filed at the Trac site, as both sites are
synchronized. (Information on Trac is however treated with less care, as Trac
is seen as the secondary site.)

https://launchpad.net/bug-repo-syncer

The program is written in the Python programming language. Development is
coordinated on Launchpad, Bazaar is the version control system, the developer
uses Eclipse and Vim to edit the program text. The Trac site lets the
developers see the bugs in the Mylyn component Eclipse.

To check out the sources, type::

       bzr branch lp:bug-repo-syncer 

