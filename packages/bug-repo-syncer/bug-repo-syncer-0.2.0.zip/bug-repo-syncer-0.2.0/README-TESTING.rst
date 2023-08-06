===============================================================================
                        Testing Bug Repo Syncer
===============================================================================

Bug Repo Syncer uses the test framework ``py.test``.

    http://pytest.org/latest/

The test suite uses the somewhat advanced feature of creating it's own command
line options. This way the password for Trac can be entered once at the start
of the test, and it is then given to each test that requires it.


Installing ``py.test``
======================

The author uses ``py.test`` with two interesting plugins:

* ``pytest-xdist``: to run multiple tests in parallel.
* ``pytest-cov``: to create reports on test coverage.

To install ``py.test`` and the plugins, get administrator privileges, and type
the following at a shell prompt::

    pip install -U pytest
    pip install -U pytest-xdist
    pip install -U pytest-cov

Or, if you prefer Easy Install type::
 
    easy_install -U pytest
    easy_install -U pytest-xdist
    easy_install -U pytest-cov

Even shorter installation instructions are at the project's website, together
with an introduction of the test framework. 

http://pytest.org/latest/getting-started.html


Useful Commands
===============

These are useful invocations to run the tests. It is a good idea to run tests
in parallel, especially because Launchpad is slow.

Run the non modifying tests with four processes. Include details about skipped
tests::

    py.test -n 4 -r s

Additionally run tests that modify Trac and Launchpad (test repositories).
There are race conditions however, and the modifying tests fail from time to
time. (There is only one instance of each repository.) ::

    py.test -n 4 -r s --modify-all 

Run all tests, even those that are really slow. (Currently there are no
dangerous tests.) Additionally show the five slowest tests. The slow tests must
be run sequentially. Options can be shortened if they remain unambiguous. ::

    py.test --slow --durations=5
    py.test --slow-and-dangerous --durations=5

Do coverage analysis with all tests::

    py.test --cov=bug_repo_syncer/ --cov-report=annotate --cov-report=term --slow


Special options
===============

``--modify-trac``
    Modify the trac server, prompts for Trac password.

``--modify-lp``
    Modify Launchpad test server, used inconsequently, because you don't
    need to enter a password to modify Launchpad. 

``--modify-all``
    Modify both Launchpad and Trac.

``--slow-and-dangerous``
    Perform time consuming, and potentially dangerous tests. Even these so
    called "dangerous" tests only access the test servers. But they might leave
    them in a broken state. Implies ``modify-all``.

    Currently all slow and dangerous tests can not be run in parallel. They are
    skipped when the test suite is run with multiple processes; for example with 
    ``-n 4``.
