Copyright (c) 2012 Jose Luis Naranjo Gomez
========================================================================
LICENSE http://www.gnu.org/copyleft/gpl.html
========================================================================
Flashcards is meant to be called from the command line.

Type "flashcards -h"into the command line once you've installed it.


========================================================================
INSTALLATION
========================================================================

FOR Windows (32-bit) 1st method:
    1) Download and install python (http://www.python.org/ftp/python/2.7/
    python-2.7.msi) with default settings.
    
    2) Open the start menu and right click Computer and select properties.
    3) Click Advanced System Settings and then click Environment Variables
    4) Open the Path variable (at the bottom of system variable, and at 
    the very end of it add a semicolon and then the path to the folder 
    where you installed python.
    
    If you installed for all users with default settings and 
    default installation folders, you would add this, for example.
    ;C:\python27
    
    5) Download and install setuptools (http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11.win32-py2.7.exe#md5=57e1e64f6b7c7f1d2eddfc9746bbaf20)
    6) Save the contents of this https://raw.github.com/pypa/pip/master/contrib/get-pip.py into a file called get-pip.py and save it on your desktop.

    7) Open up the command line (It's called cmd, look for it in the start menu).
    8) Enter the following:
        cd Desktop
        python get-pip.py
        pip install pyflashcards
    9) Everything should be installed! Try the second method if you run int
    and problems.
    
FOR Windows (32-bit) 2nd method:
    1) Download and install python (http://www.python.org/ftp/python/2.7/
    python-2.7.msi) with default settings.
    2) Download and install argparse (http://pypi.python.org/packages/any/a/argparse/argparse-1.1.win32.msi#md5=1bad87b66962668c626fa4e843f7d335)
    3) Download and install 
----------------------------------------------------------------------------
For Mac and Linux:
    1) Open up the terminal
    2) Enter the following two commands:
        sudo curl http://python-distribute.org/distribute_setup.py | python
        sudo curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
    If you get an error for either of these two, remove the word sudo and 
    try it again.
    3) Enter one more command:
        sudo pip install flashcards
    4) You are done!
========================================================================
GENERAL USAGE
========================================================================
Once you've installed the program
    1) Open up 'cmd' if you are on Windows computer, or the 'terminal' if you are
    on a Mac or Linux computer.
    2) Enter "flashcards" or "flashcards --help" for more info.

When you are adding answers in the program, you can add multiple choices.
    Seperate every possible answer with a comma.
    
CSV MODE AND SQL MODE

1) CSV - Comma Separated Values
This mode creates a data.csv file in the current working directory (defa
ult is home folder).

Advantages:
    Easier to edit by yourself - without the program
    More portable
    
If you want to edit your flashcards yourself:
    Open the data.csv file, which is probably in your home folder.
    Each line contains a question and it's answer/s.
    The first value is the question, and the rest of the values in that
        line are the answers.
    Each value is separated by commas. Spacing matters, so be careful.

2) SQL - Database storage
This mode creates a ".flashcards.db" file in your home folder.

Advantages:
    Allows for storing SETS of flashcards.
    Provides a more advanced editor.
    Better for long term storage.

========================================================================
CHANGESv2.2 (current)
========================================================================
1) MAJOR: Implemented sqlite3 database option.
2) initial menu asks if the user wants a sqlite3db in their home directo
ry OR a csv file in their cwd.
3) This leads them to the corresponding quiz. This means that there are 
two bundled version of the quiz. 
4) The quiz_sql.py script relies on db_api, a script a sqlite3 framework
class designed for the quizzes' use.
5) Implemented csv.writer to writer() class in quiz_csv.
6) Switching zipped lists to a dictionary in csv quiz.
7) Added flags for CLI args.


========================================================================
CHANGESv2.0
========================================================================
1) Implemented CSV.reader succesfully to reader class. Data is stored in
    data.csv now.
2) Collapsed quiz_creator.py and quiz.py into quiz.py - they are both no
w classes.
3) Updated documentation.
4) Brought back __main__.py
5) Commented important code
6) No known bugs

========================================================================
CHANGESv1.2
========================================================================
1) Removed append mode (write only now).
2) Reverted a bunch of changes - flashcards just wasn't ready yet for th
    implementations.
    
========================================================================
CHANGESv1.1
========================================================================
1) Added append mode for quiz_maker.py and gave it a menu.
2) Fixed incorrect package name in README.txt
3) Moved menu.py to __init__.py
4) Added line breaks to menu UI in __main__.py
5) Improved error handling with semantic errors.
6) Improved documentation
7) Commented on some code

========================================================================
FUTURE IDEAS
========================================================================
1) Replace zipped lists of qna with a dictionary.
2) Provide sound and graphics with pygame
3) Provide a cross-platform GUI with pyGTK+
4) Provide a browser version with Django


Source: https://launchpad.net/pyflashcards or http://pypi.python.org/pypi/pyflashcards/2.2
