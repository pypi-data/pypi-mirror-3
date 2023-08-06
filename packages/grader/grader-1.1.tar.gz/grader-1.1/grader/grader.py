#!/usr/bin/env python

import os
from sys import exit
import time
import settings
"settings.project_data is a dict of conf settings"#{'project 3': {'docs': ['exercise 1', 'exercise 2', 'exercise 3']}, 'project 2': {'docs': 'ex1'}}
"settings.student_data is a dict of {'first_name':item[0],'last_name':item[1],'period':item[2]}"
"settings.student_files is a dict with keys of folders and values of lists of files names" #Example on next line!
#{'oglesby project 3': [], 'pobre project 3': [], 'naranjo project 3': ['naranjo exercise 1', 'naranjo exercise 2', 'naranjo exercise 3']} student_files example!

def safety():
    if not os.path.isdir(settings.ROOT):
        settings.setup()
        print "Setting up..."
        exit(0)
safety()

try:
    project_names = [k.lower() for k in settings.project_data] # A list of project folder names that should exist after each students last name (in lowercase)
    student_folders = [x.lower() for x in os.listdir(settings.student_files_path)] # A list of existing folders (in lowercase)
    lastnames = [x['last_name'].lower() for x in settings.student_data] #A list of the lastnames of every student (in lowercase)
except:
    print "Error in global variables @ '%s'" % __file__

def get_theory_files():
    "Returns a list of list. sets of theoretical files generated with lastnames and project_data"
    theory = []
    lastnames = [x['last_name'].lower() for x in settings.parse_student_data()]
    for name in lastnames:
        for setting in settings.get_project_data():
            temp = settings.get_project_data()[setting]['docs']
            scripts = [name+" "+x for x in temp]
            for script in scripts:
                theory.append(script)

    return theory

def validate_folders():
    "Checks to see if the project folder is for each student - returns a list of missing folders" #WORKING
    missing = []
    for project in project_names:
        theoretical_folders = [name + " " + project for name in lastnames]
        for folder in theoretical_folders:
            if folder not in student_folders: missing.append(folder)
    return missing

def validate_files():
    "Looks into the project folders of each student and checks to see if the required files exist. Returns a list of missing files."
    theory = get_theory_files()
    files = settings.get_student_files()
    missing = []
    for script in theory:
        if script not in files: missing.append(script)
    return missing

def debug():
    print "Project Names  :\t",project_names
    print "Actual folders :\t",student_folders
    print "Last names all :\t",lastnames
    print "Missing folders:\t",validate_folders()
    print "Missing files  :\t", validate_files()

def register():
    open(settings.student_info_path,'a')
    txt = open(settings.student_info_path,'r+')
    content = txt.readlines()
    txt.truncate(0)
    first_name = raw_input("First name of student: ")
    last_name = raw_input("Last name of student  : ")
    period =    raw_input("Class day of student  : ")
    statement = "%s %s %s\n" % (first_name,last_name,period)
    content.append(statement)
    final = ''
    for line in content:
        final += line
    txt.write(final)
    txt.close()

def watcher():
    missing_files = validate_files()
    missing_folders = validate_folders()
    buff = ''
    say = []
    if missing_files:
        say.append("\nMISSING FILES:")
        for fname in missing_files:
            f = fname.split()
            name = settings.first_name(f[0])+" "+f[0]
            period = settings.class_period(f[0])
            if len(f) > 2: val = f[1]+' '+f[2]
            else: val = f[1]
            
            say.append("%s (%s) is missing %s." % (name,period,val))

    else: say.append("All files are turned in correctly!")
    if missing_folders:
        say.append("\nMISSING FOLDERS")
        for fname in missing_folders:
            f=fname.split()
            name = settings.first_name(f[0])+" "+f[0]
            period = settings.class_period(f[0])
            if len(f) > 2: val = f[1]+' '+f[2]
            else: val = f[1]
            say.append("%s (%s) is missing %s." % (name,period,val))
    else: say.append("All folders are turned in correctly!")
    return '\n'.join(say)

def grade():
    safety()
    buff="="*72
    output = buff+"\n"+time.asctime()+"\n"+buff+"\n"+watcher()+"\n\n"
    log_path = os.path.join(settings.ROOT,'log.txt')
    log = open(log_path,'a')
    log.write(output)
    log.close()
    

def menu():
    print "1:\tRegister a new student"
    print "2:\tRun diagnostics (make sure folders are in %s" % settings.student_files_path
    ask = raw_input("> ")
    if ask == '1': register()
    if ask == '2': grade()
if __name__ == "__main__":
    menu()
