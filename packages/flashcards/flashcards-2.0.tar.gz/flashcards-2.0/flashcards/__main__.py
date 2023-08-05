from sys import exit
import quiz

def delete():
    print "Are you sure (Y/N)?"
    ask = raw_input("> ").lower()
    if ask == 'n' or ask == 'no':
        exit(0)
    else:
        txt = open(quiz.data_path, 'w')
        txt.truncate()
        txt.close()
        
def menu():
    print "\tType 'exit' to exit program and 'end' to break loop\n"
    while True:
        print "1: Enter quiz mode"
        print "\tflashcards.quiz.reader()"

        print "2: Enter quiz editor"
        print "\tflashcards.quiz.writer()"

        print "3: Erase current quiz"
        print "\tflashcards.delete()"
        ask = raw_input("> ").lower()
        
        print "="*72,"\n"
        
        if ask == 'end':
            break
            
        if ask == 'exit':
            exit(0)
            
        if ask == '1' or ask == "enter quiz mode":
            quiz.reader()
            
        if ask == '2' or ask == 'enter quiz editor':
            quiz.writer()
            
        if ask == '3' or ask == 'erase current quiz':
            delete()

if __name__ == "__main__":
    menu()
