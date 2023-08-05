import sys
import os
from random import shuffle

cwd = os.getcwd()
sys.path.append(cwd)

import data

def start():
    key = zip(data.questions, data.answers)
    shuffle(key)
    for entry in key:
        question = entry[0]
        answer = entry[1]
        correct = False
 

        print question
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
                
                print "\tAny of the following:"
                print "\t",' | '.join(temp)
                
            if isinstance(answer, str):
                print answer
        print "="*72
    print "You have gone through each entry in the list!"


if __name__ == "__main__":    
    start()
