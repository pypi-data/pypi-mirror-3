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
    documents = os.path.join(home_path, 'Documents')
    ROOT = os.path.join(documents, 'grader')

ROOT
student_info_path = os.path.join(ROOT,'students.txt')
student_files_path = os.path.join(ROOT,'student_files')
grader_settings_path = os.path.join(ROOT,'grader_settings.conf')

def setup():
    "Creates a folder in the Documents folder \"(grader)\"of the OS, for data persistence."
    if not os.path.isdir(ROOT):
        os.mkdir(ROOT)
        temp = open(student_info_path,'a') #Creates a file at this path ^ if not existent.
        temp.close()
        del temp
    if not os.path.isdir(student_files_path):
        os.mkdir(student_files_path)
        temp = open(grader_settings_path,'a')
        temp.close()
        del temp


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

def get_project_data(path):
    config = ConfigObj(grader_settings_path)
    return config

if os.path.isdir(ROOT):
    try:
        student_data = parse_student_data()
    except:
        print "Error parsing student folders\nmake sure that there are no blank lines in the students.txt file".upper()

    try:
        project_data = get_project_data(grader_settings_path)
    except:
        print "Error parsing project data".upper()

    try:
        student_files = get_student_files()
    except:
        print "Error parsing student files".upper()
