import os
import sys

#Current working directory
cwd = os.getcwd()
#Adds the cwd to the PYTHONPATH
sys.path.append(cwd)
#Path to the data file
data_path = os.path.join(cwd, 'data.py')

#Creates a data.py file in the cwd if there isn't already one there.
BALLS = open(data_path,'a')
BALLS.close()



#-----------------------------------------------------------------
#For sending messages to the user.
def msg(message):
    print "="*72
    print message
    print "="*72

#This function parses the questions and answers lists and writes them to
#the data.py file in the cwd.
def writer(mode):

    txt = open(data_path,"r+")
    
    if mode == 'write':
        open(data_path, "w").truncate()
    
    txt.write("questions = [\n")
    
    for q in questions:
        txt.write("\"%s\",\n" % q)
        
    txt.write("]\n\n")
    
    txt.write("answers = [\n")
    
    #For handling tuples and strings in the answers, for multiple choice questions
    for a in answers:
        if isinstance(a,str):
            txt.write("\"%s\",\n" % a)        
        if isinstance(a,tuple):
            txt.write("(")
            for t in a:
                txt.write("\"%s\"," % t)
            txt.write("),\n")
    txt.write("]")

#Asks if the user if he/she would like to create a new quiz (Write Mode)
#or if they would like to add to an existing one in the cwd (Append Mode)
def mode_finder():
    print "1: Append mode"
    print "2: Write mode (for creating initial file)"
    print "\tWARNING: Write Mode deletes contents of data.py if"
    print "\tit exists in the current working directory."
    
    ask = raw_input("> ")
    
    
    if ask == '1' or ask.lower() == "Append mode".lower():
        return 'append'
        
    if ask == '2' or ask.lower() == "Write mode".lower():
        return 'write'
        
    else:
        print "Error in mode_finder()"
        return 'append'




def collector():
    #Result of mode_finder() stored here
    mode = mode_finder()
    
    if mode == 'write':    
        questions = []
        answers = []
        global questions
        global answers
        print "WARNING:\n\tIf data.py exists, it will be replaced."
        print "\tIf it doesnt exist, it will be created."
        print "\tProceed? (Y/N)?"
        check = raw_input("> ").lower()
        if check == 'n':
            sys.exit(0)

    if mode == 'append':
        
        print "\nNOTE:\nAppend mode only adds questions to the quiz."
        print "To remove questions, you need to do it manually\n for the time being."
        #Since append mode has been chosen, script tries to import the allegedly stored quiz.
        try:
            import data
            questions = data.questions
            answers = data.answers
        except:
            msg("data.py not found!")
            sys.exit(0)
        
    #For getting the questions and the answers from the user.
    while True:
        #NOTE:
        #raw_input()
        question = raw_input("Question:\t")
        if question == 'exit' or question == 'end':
            break
        #input() - for tuple handling
        answer = input("Answer  :\t")
        if answer == 'exit' or answer == 'end':
            break
            
        questions.append(question)
        answers.append(answer)
        
        msg("NEW SECTION")
    writer(mode)

def start():
    collector()

if __name__ == "__main__":
    start()
