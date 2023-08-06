import os
import settings
from pprint import pprint
"settings.project_data is a dict of conf settings"#{'project 3': {'docs': ['exercise 1', 'exercise 2', 'exercise 3']}, 'project 2': {'docs': 'ex1'}}
"settings.student_data is a dict of {'first_name':item[0],'last_name':item[1],'period':item[2]}"
"settings.student_files is a dict with keys of folders and values of lists of files names" #Example on next line!
#{'oglesby project 3': [], 'pobre project 3': [], 'naranjo project 3': ['naranjo exercise 1', 'naranjo exercise 2', 'naranjo exercise 3']} student_files example!


project_names = [k.lower() for k in settings.project_data] # A list of project folder names that should exist after each students last name (in lowercase)
student_folders = [x.lower() for x in os.listdir(settings.student_files_path)] # A list of existing folders (in lowercase)
lastnames = [x['last_name'].lower() for x in settings.student_data] #A list of the lastnames of every student (in lowercase)

def get_theory_files():
    "Returns a list of list. sets of theoretical files generated with lastnames and project_data"
    theory = []
    for name in lastnames:
        for setting in settings.project_data:
            temp = settings.project_data[setting]['docs']
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
    files = settings.student_files
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
    txt = open(settings.student_info_path,'a+r')
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
    buff = "="*72
    if missing_files:
        print buff,"\nMISSING FILES:"
        for fname in missing_files:
            f = fname.split()
            name = settings.first_name(f[0])+" "+f[0]
            period = settings.class_period(f[0])
            if len(f) > 2: val = f[1]+' '+f[2]
            else: val = f[1]
            
            print "%s (%s) is missing %s." % (name,period,val)
        print buff

    else: print "All files are turned in correctly!"
    if missing_folders:
        print buff,"\nMISSING FOLDERS\n"
        for fname in missing_folders:
            f=fname.split()
            name = settings.first_name(f[0])+" "+f[0]
            period = settings.class_period(f[0])
            if len(f) > 2: val = f[1]+' '+f[2]
            else: val = f[1]
            print "%s (%s) is missing %s." % (name,period,val)
            print buff
    else: print "All folders are turned in correctly!"

if __name__ == "__main__":
    watcher()
