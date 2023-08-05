from sys import exit
import quiz
import data
import quiz_maker

def delete():
    print "Are you sure (Y/N)?"
    if raw_input("> ").lower() == 'n':
        exit(0)
    else:
        txt = open('data.py', 'w')
        txt.truncate()


def menu():
    print "1: Enter quiz mode"
    print "\tflashcards.quiz.start()"

    print "2: Enter quiz editor"
    print "\tflashcards.quiz_maker.start()"

    print "3: Erase current quiz"
    print "\tflashcards.delete()"
    ask = raw_input("> ").lower()
    
    if ask == '1' or ask == "enter quiz mode":
        quiz.start()
        
    if ask == '2' or ask == 'enter quiz editor':
        quiz_maker.start()
        
    if ask == '3' or ask == 'erase current quiz':
        delete()

if __name__ == "__main__":
    menu()