Python Selenese translator
==========================

Selenium IDE lets you create Selenium tests in specially structured HTML (or
"Selenese"). These can be easily run on your local machine but do not lend
themselves to being run on a server via e.g. Selenium RC.

This dynamically translates suites of Selenese tests into Python
unittest.TestCase classes, which can then be run using Selenium RC within 
the standard Python unit testing framework and using the Python Selenium 
bindings.


Warning
-------

This code is still under construction. It might break randomly and does not 
currently support more than a fraction of Selenese keywords. If you'd like to
improve its behaviour then please add more methods to the class in mapper.py
to map Selenese keywords to Python-binding API calls.

Setup
-----

1. Download Selenium RC http://seleniumhq.org/download/

2. Unpack the server JAR at selenium-server-X/selenium-server.jar and run it
in the background:

 java -jar selenium-server.jar

3. Check out this repository anywhere on your filesystem.

4. Unpack the Python bindings selenium-python-client-driver-X/selenium.py 
from Selenium RC and place it within this repository


Execution
---------

A `test.py` example file is provided, where it shows how to run tests from
files. You can alternatively use a `SingleStringAdaptor` to create tests from
a single string.

If your target is to build tests from a folder (or a set of folders), take
a look at the usage of the `generate_test_case` function in combination with
the `TestSuiteFileAdaptor`.

Testing
-------

Functional testing is implemented through Selenese tests.

 python test.py [selenium-server]

Known issues
------------

The main issue is that not all of Selenium's test syntax has been transcribed
in mapper.py yet. Please let me know if your tests fail on a particular 
Selenium keyword; alternatively, feel free to fork the github repository and 
add the mapping yourself.

Credits
-------

All the mapper.py functions were created by J.P. Stacey. Development on
PySelenese seems to have halted two years ago. I just needed something to
translate a HTML Selenese string and this is the best project I've found.

Some heavy refactoring needed to take place though, but the heavy part(map
the Selenese functions to Python in real time) was already done by Stacey.

Here is the original repo:

 http://github.com/jpstacey/PySelenese
