import os
import csv

cwd = os.getcwd()
data_path = os.path.join(cwd, 'data.csv')
global data_path

#Creates a data.csv file in the current working directory if it does not already exist.
open(data_path,'a')

class reader(object):
    """This class actually quizzes the user. It parses from data.csv which is created in the current working directory.
    It runs itself, so you just need to call reader() and it will read the data file in the cwd and quiz the user on it.
    """
    
    def __init__(self):
        self.txt = open(data_path, 'r')
        self.reader = csv.reader(self.txt, delimiter=",")
        #questions - list of strings
        #answers - list of tuples with strings in them
        #KEY is zip(questions, answers)
        self.KEY = self.load() #Parses the information in ./data.csv and stores it in a friendlier format.
        self.start() #Gets the ball rolling. start() is the quiz
        
    def msg(self,message):
        print "="*72
        print message
        
    def load(self):
        answers = []
        questions = []
        
        for row in self.reader:
            if not row:
                print "No data!"
            if len(row) > 2:
                multiple_choice = True
            else:
                multiple_choice = False
                
            #Defining the answer as a list
            if multiple_choice:
                answer = row[1:]
            
            if not multiple_choice:
                answer = [row[1]]
                
            question = row[0]
            #Adding that set of qna to the list
            questions.append(question)
            answers.append(answer)
            
        key = zip(questions, answers)
        return key
        
    def start(self):
        for each in self.KEY:
            question = each[0]
            answers = each[1]
            self.msg("Question:\t%s" % question)
            attempt = raw_input("> ")
            
            for answer in answers:
                if attempt == answer:
                    correct = True
                    break
                else:
                    correct = False
            
            if correct:
                print "Correct!"
            if not correct:
                print "The correct answer was:"
                if len(answers) > 1:
                    print "\tany of the following:"
                    
                print "\t",' | '.join(answers)
                
        print "="*72

class writer(object):
    """This class appends sets of questions and answers into the data.csv file
    in the current working directory. The reader() class above uses this file."""
    
    def __init__(self):
        #File IO object in either 'a' or 'w' mode.
        self.txt = open(data_path,'a')
        #KEY is a list of tuples with strings in them. Each tuple is a pair of question and answer.
        self.KEY = self.get_key() #Gets the questions and answers from the user and stores them in self.KEY for self.start()
        self.write() #Gets the ball rolling. write() is the function that actually writes information to ./data.csv
        
    def write(self):
        for group in self.KEY:
            question = group[0]
            answer = group[1].split(",")
            
            format = question+","
            
            for each in answer:
                format += "%s," % each
            format = format[:-1]
            self.txt.write("%s\n" % format)
            #self.txt.write("%s,%s" % question, answer)
        self.txt.close()

    def get_key(self):
    
        questions = []
        answers = []
        
        print "="*72
        print "NOTE:\tSeparate multiple choice answers with commas."
        
        while True:
            print "="*72
            
            question = raw_input("Question:\t ")
            
            if question == 'exit' or question == 'end':
                break
            
            answer = raw_input("Answer/s:\t")
            if answer == 'exit' or answer == 'end':
                break
                

            questions.append(question)
            answers.append(answer)
        key = zip(questions, answers)
        print "\n"
        return key
        
        
    def get_mode(self):
        print "1: Edit mode"
        print "2: Over-write mode"
        
        mode = raw_input("> ")
        
        cwd = os.getcwd()
        data_path = os.path.join(cwd, 'data.csv')
        txt = open(data_path,'a')
        if mode == '1' or mode == 'edit mode':
            txt = open(data_path,'a')
            mode = 'edit'
        if mode == '2' or mode == 'over-write mode':
            txt = open(data_path,'w')
            mode = 'over-write'
            
        print "Opening %s in %s mode..." % (os.path.join(os.getcwd(), 'data.csv'), mode)

        return txt
        

