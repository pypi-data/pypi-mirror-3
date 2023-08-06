import sys
import os
import dircache
from configobj import ConfigObj
from shutil import rmtree

platform = sys.platform
home_path = os.path.expanduser("~")

if platform == 'linux2' or platform == 'darwin':
    documents = os.path.join(home_path, 'Documents')
    ROOT = os.path.join(documents, 'grader')

if platform == 'win32':
    documents = os.path.join(home_path, 'My Documents')
    ROOT = os.path.join(documents, 'grader')
    bin_fname = 'grader.bat'
    bin_path = os.path.join(ROOT,bin_fname)

student_info_path = os.path.join(ROOT,'students.txt')
student_files_path = os.path.join(ROOT,'student_files')
grader_settings_path = os.path.join(ROOT,'grader_settings.conf')
readme = os.path.join(ROOT,'README.txt')
readme_local = "README"

def set_defaults():
    temp = open(readme,'w')
    temp2 = open(readme_local,'r')
    docs = temp2.readlines()
    doc = ''.join(docs)
    temp.write(str(doc))
    temp.close()
    temp2.close()
    sample_log = open(os.path.join(ROOT,'log.txt'),'a')
    sample_log.write("Congratulations! You have succesfully set up grader.\n\n\n")
    sample_log.close()
    
def setup():
    "Creates a folder in the Documents folder \"(grader)\"of the OS, for data persistence."
    if not os.path.isdir(ROOT):
        os.mkdir(ROOT)
        temp = open(student_info_path,'a') #Creates a file at this path ^ if not existent.
        temp.write("Luis Naranjo 3B")
        temp.close()
        del temp
    if not os.path.isdir(student_files_path):
        os.mkdir(student_files_path)
        set_defaults()
        template_folder=os.path.join(student_files_path,'naranjo project 3')
        os.mkdir(template_folder)
        temp1 = open(os.path.join(template_folder,'naranjo exercise 1'),'a')
        temp2 = open(os.path.join(template_folder,'naranjo exercise 2'),'a')
        temp1.close()
        temp2.close()
        temp = open(grader_settings_path,'a')
        temp.write("[project 3]\n")
        temp.write("docs = exercise 1,exercise 2")
        temp.close()
        del temp
        if platform == 'win32':
            temp = open(bin_path,'a')
            temp.write("grade")
            temp.close()


def teardown():
    "Deletes all files in ROOT dir, as well as the ROOT dir."
    #WARNING - deletes all files under ROOT
    if os.path.isdir(ROOT):
        rmtree(ROOT)

def parse_student_data():
    "Returns a list of dicts of student information"
    data = []
    try:
        txt = open(student_info_path,"r+")
        info = txt.readlines()
    except IOError:
        print "Error when trying to read %s." % student_info_path

    for each in info:
        item = each.split()
        temp={'first_name':item[0],'last_name':item[1],'period':item[2]}
        data.append(temp)

    return data

def first_name(name):
    name = name.lower()
    data = parse_student_data()
    for entry in data:
        first = entry['first_name'].lower()
        last = entry['last_name'].lower()
        if last == name: return first

def class_period(name):
    name = name.lower()
    data = parse_student_data()
    for entry in data:
        first = entry['first_name'].lower()
        last = entry['last_name'].lower()
        period = entry['period']
        if name == first or name == last: return period

def get_student_files():
    "Returns a dict with lists of files names - keys are folder names" #Working
    files = []
    for folder in [os.path.join(student_files_path,x) for x in os.listdir(student_files_path)]:
        temp_files = dircache.listdir(folder)
        [files.append(f) for f in temp_files]
    return files

def get_project_data():
    config = ConfigObj(grader_settings_path)
    return config


if os.path.isdir(ROOT):
    try:
        student_data = parse_student_data()
    except:
        print "Error parsing student folders\nmake sure that there are no blank lines in the students.txt file".upper()

    try:
        project_data = get_project_data()
    except:
        print "Error parsing project data".upper()

    try:
        student_files = get_student_files()
    except:
        print "Error parsing student files".upper()
