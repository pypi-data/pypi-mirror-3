import sys
import os
from random import shuffle

cwd = os.getcwd()
sys.path.append(cwd)

import data

def start():
    try:
        key = zip(data.questions, data.answers)
    except AttributeError:
        print "You need to create a data.py answer key first!"
        sys.exit(0)
    shuffle(key)
    
    print "="*72
    for entry in key:
        question = entry[0]
        answer = entry[1]
        correct = False
 
        print "Question:\t%s" % question
        reply = raw_input("> ")
        
        if isinstance(answer, tuple):
            for each in answer:
                if each == reply:
                    correct = True
                    
        if isinstance(answer, str):
            if answer == reply:
                correct = True
                
        if correct:
            print "Correct!"
            
        if not correct:
            print "The correct answer was:"
            
            if isinstance(answer, tuple):
                temp = []
                for each in answer:
                    temp.append(each)
                
                print "\tany of the following:"
                print "\t",' | '.join(temp)
                
            if isinstance(answer, str):
                print answer
        print "="*72
    print "\n\nYou have gone through each entry in the list!"


if __name__ == "__main__":    
    start()
