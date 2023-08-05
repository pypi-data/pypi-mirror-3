import os
from sys import exit
from random import shuffle
import db_api

home_path = os.path.expanduser("~")
path = os.path.join(home_path,".flashcards.db")
db = db_api.db_op(path)

#db.refresh() #Reloads db info

#print db.index #List of all of the tables in the db
#db.select_tbl(msg) #Menu for choosing a table in the db, returns table name

#   TABLE METHODS
#db.create_tbl(name) #Creates a table in the db
#db.delete_tbl(name=None) #Deletes a table in the db
#db.delete_all() #Deletes all of the tables in the db

#   VALUE METHODS
#db.write_to_tbl(id,question,answer,table) #For inserting values to a table
#db.read_from_tbl(table=None) #Retuns list of tuples from that table. Each tuple is a set -  (id, question, answer)
#db.delete_from_tbl(table=None) #Deletes a value in the table
#db.print_values(table=None) #Prints all of the values in the table

#db.con.commit()
#db.close()
#list_tables() #Lists all available tables

def msg(message):
    print "="*72
    print message
    
#========================================================================

def use_set(table=None):
    if not table:
        table = db.select_tbl("use")
        
    key = db.read_from_tbl(table)
    
    if not key:
        msg("No flashcards stored in this set!")
        
    shuffle(key)
    
    breakers = "end exit break close leave stop".split()
    
    for each in key:
    
        ID = each[0]
        question = each[1]
        answer = str(each[2])
        answers = answer.split(",")
        
        print "\t\tQUESTION #%d" % ID
        print "Question:\t%s" % question
        response = raw_input("> ")
        
        if response in breakers:
            break
            
        correct = False
        for the_answer in answers:
            if response == the_answer:
                correct = True
        
        
        if correct:
            print "\nCorrect!"
       
        if not correct:
            print "\nThe correct response was any of the following:"
            answers = " | ".join(answers)
            print "\t",answers
        print "-"*72
        
def create_set(name=None):
    if not name:
        print "What would you like this set of flashcards to be called?"
        print "No spaces or odd characters allowed!"
        name = raw_input("> ")
        
    db.create_tbl(name)


def edit_set(question,answer,table=None):
    if not table:
        table = db.select_tbl("edit")


    entries = db.read_from_tbl(table) #Retuns list of tuples from that table. Each tuple is a set -  (id, question, answer)
    if len(entries) == 0:
        current_id = 1
    if len(entries) > 0:
        entry_ids = []
        for entry in entries:
            ID = entry[0]
            entry_ids.append(ID)
        entry_ids.sort()
        current_id = len(entries) + 1
        
    #current_id = int(raw_input("ID:\t"))
    #question = raw_input("Question:\t")
    #answer   = raw_input("Answer:  \t")
    
    db.write_to_tbl(current_id,question,answer,table)
        



def erase_set():
    table = db.select_tbl("erase")
    db.delete_tbl(table)
    return table
    
def erase_all_sets():
    
    db.refresh()
    print "Deleted the following sets of flashcards:"
    for table in db.index:
        print "\t%s" % table
    db.delete_all()
    
def close():
    db.close()
    exit(0)
