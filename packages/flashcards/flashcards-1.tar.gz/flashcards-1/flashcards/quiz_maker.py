import os
import sys

cwd = os.getcwd()
sys.path.append(cwd)
data_path = os.path.join(cwd, 'data.py')

BALLS = open(data_path,'a')
BALLS.close()

questions = []
answers = []

#-----------------------------------------------------------------

def msg(message):
    print "="*72
    print message
    print "="*72

def writer():

    open('data.py','w')
    txt = open(data_path,"r+")
    txt.truncate()
    
    txt.write("questions = [\n")
    
    for q in questions:
        txt.write("\"%s\",\n" % q)
        
    txt.write("]\n\n")
    
    txt.write("answers = [\n")
    
    for a in answers:
        if isinstance(a,str):
            txt.write("\"%s\",\n" % a)        
        if isinstance(a,tuple):
            txt.write("(")
            for t in a:
                txt.write("\"%s\"," % t)
            txt.write("),\n")
    txt.write("]")



def collector():

    while True:
        question = raw_input("Question:\t")
        if question == 'exit' or question == 'end':
            break
        answer = input("Answer  :\t")
        if answer == 'exit' or answer == 'end':
            break
            
        questions.append(question)
        answers.append(answer)
        
        msg("NEW SECTION")
    writer()

def start():
    print "WARNING:\n\tThis making a new quiz will replace any old quiz in data.py"
    print "\tProceed? (Y/N)?"
    check = raw_input("> ").lower()
    if check == 'n':
        sys.exit(0)

    collector()

if __name__ == "__main__":
    start()
