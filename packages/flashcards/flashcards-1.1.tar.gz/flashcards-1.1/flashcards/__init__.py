from sys import exit
import quiz_maker
import quiz
import data


def delete():
    print "Are you sure (Y/N)?"
    if raw_input("> ").lower() == 'n':
        exit(0)
    else:
        txt = open('data.py', 'w')
        txt.truncate()


def menu():
    print "1: Enter quiz mode (keyword = enter)"
    print "\tflashcards.quiz.start()\n"

    print "2: Edit/create quiz in current directory (keyword = edit)"
    print "\tflashcards.quiz_maker.start()\n"

    print "3: Erase quiz in current directory (keyword=erase)"
    print "\tflashcards.delete()\n"
    
    ask = raw_input("> ").lower()

        
    if ask == '1' or ask == "enter quiz mode" or ask == 'enter':
        quiz.start()
        
    if ask == '2' or ask == 'enter quiz editor' or ask == 'edit':
        quiz_maker.start()
        
    if ask == '3' or ask == 'erase current quiz' or ask == 'erase':
        delete()

    return ask

while True:
    print "'exit' or 'end' to break loop."
    
    ask = menu()
    if ask == 'end':
        break
        
    if ask == 'exit':
        exit(0)
