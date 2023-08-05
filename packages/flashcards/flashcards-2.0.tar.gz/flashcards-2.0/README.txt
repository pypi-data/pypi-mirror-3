Copyright (c) 2012 Jose Luis Naranjo Gomez
========================================================================
LICENSE http://www.gnu.org/copyleft/gpl.html
========================================================================
Flashcards is meant to be used as an installed python module.

You're supposed to use it by opening the python shell and importing 'fla
shcards'. It's designed to be used after setup.py install. It will store
quizzes in the current directory (default is home directory).

Flashcards has three components:

quiz.py - data.csv - __main__.py


========================================================================
INSTALLATION
========================================================================
Use:
    python setup.py install
That should do the trick.


========================================================================
GENERAL USAGE
========================================================================
NOTE:
importing flashcards creates a data.csv file in the current working directory.
flashcards uses this file to store flashcard information.
flashcards may truncate the existing data.py, so be careful with your quizzes.

If installed:
    in the python shell:
        import flashcards
        #That should activate the menu UI
    
If not installed:
    Run __main__.py in flashcards/flashcards

ALSO:

For changes to take effect when editing data.py, you need to exit the program and re-enter.
========================================================================
1)quiz.py

    This is the main script. It has two classes:
    
    A) reader - class
    This class parses the information from the data.csv and uses it to quiz 
    the user on it.
    
    B)writer - class
    This class collects the questions and answers from the user and stores them
    in the data.csv file for the reader class to use later.
    
2)data.csv (data.|C|omma|S|eparated|V|alues)

    This is the data file where all of the flashcard information is stored.
    You can add information to it yourself, or you can use quiz.writer()
    
    Each line in this file contains a question and it's corresponding answer/s.
    
    Each value in each line is separated by a comma, so be carefull with questions
    and answers that have commas in them.
    
    The first value in the line is always the question, and whatever values that follow
    in that line are the various possible answers.
    
    Make sure there are no blank lines. Remember that spacing counts.
    "answer" is not the same as " answer"
    

3) __main__.py

    Just a menu interface for user convenience, it makes use of all the scripts in the package.
    It also includes a delete function, which erases the contents of the data.csv file
    in the current working directory.
    
========================================================================
CHANGESv2.0 (current)
========================================================================
1) Implemented CSV module succesfully. Data is stored in data.csv now.
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
