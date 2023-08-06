import os
import sys
import shutil
import logging
from dircache import listdir
from datetime import datetime

from configobj import ConfigObj

#log = True
#capitalization = 'lower'  # Styles: lower, upper, capitalize, title

home = os.path.expanduser('~')
source_root = os.path.abspath(os.path.dirname(__file__))
skeleton_grader = os.path.join(source_root, 'skeleton_grader')


if sys.platform == 'win32':
    documents = os.path.join(home, 'My Documents')

if sys.platform in ['linux2', 'darwin']:
    documents = os.path.join(home, 'Documents')

project_root = os.path.join(documents, 'grader')


if not os.path.isdir(project_root):
    shutil.copytree(skeleton_grader, project_root)
    #shutil.copy  # TODO: Copy README.rst to project_root

settings_path = os.path.join(project_root,'settings.conf')
students_path = os.path.join(project_root, 'students.txt')
log_path = os.path.join(project_root, 'log.txt')
grader_path = os.path.abspath(os.path.join(project_root, 'grader_files'))

for filepath in [settings_path, students_path, log_path]:
    try:
        assert os.path.isfile(filepath)
    except AssertionError, error:
        print error

config = ConfigObj(settings_path)
#{'project 3': {'exercise 1': ['.jpg', '.3dm'], 'exercise 2': '.3dm'}}

if 'show members' in config:
    show_members = config['show members']
    if show_members.lower() == 'true':
        show_members = True
    if isinstance(show_members, str):
        if show_members.lower() == 'false':
            show_members = False

else:
    show_members = True

if 'capitalization' in config:
    capitalization = config['capitalization']

else:
    capitalization = 'lower'

if 'log' in config:
    log = config['log']

    if log.lower() == 'true':
        log = True
    if isinstance(log, str):
        if log.lower() == 'false':
            log = False

else:
    log = False

if log:
    logging.basicConfig(format='%(message)s', filename=log_path)

if not log:
    logging.basicConfig(format='%(message)s')

students = []
#[('Luis Naranjo', ' 3B'), ('Miguel Pobre', ' 3B'), ('Christina Oglesby', None)]

with open(students_path) as fh:
    students = [line.strip() for line in fh.readlines()]

if log:
    date = datetime.now().strftime('%B %d %Y %I:%M %P')
    entry_title = "log entry on %r" % date
    logging.warning(entry_title)


def rename_all( root, items):
    for name in items:
        formatted = getattr(name, capitalization)()
        try:
            os.rename( os.path.join(root, name), 
                                os.path.join(root, formatted))
        except OSError:
            pass # can't rename it, so what

    # starts from the bottom so paths further up remain valid after renaming
for root, dirs, files in os.walk(grader_path, topdown=False ):
    rename_all(root, dirs )
    rename_all(root, files)

warnings = []
        

for project in config:
    if not isinstance(config[project], dict): continue
    for lastname in students:
        lastname = lastname.lower()
        exercises = config[project]  # {'exercise 1': ['.jpg', '.3dm'], 'exercise 2': '.3dm'}
        expected_foldername = '%s %s' % (lastname, project)
        expected_foldername = getattr(expected_foldername, capitalization)()
        expected_folder = os.path.join(grader_path, expected_foldername)
        if not os.path.isdir(expected_folder):
            print expected_folder
            warning = "%s is missing the '%s' folder." % (lastname, project)
            warnings.append(warning)
            if not show_members: continue

        for exercise in exercises:
            extensions = exercises[exercise]
            if isinstance(extensions, str):
                extensions = [extensions]

            assert isinstance(extensions, list)

            for ext in extensions:
                expected_exercise_name = '%s %s' % (lastname, exercise)
                expected_exercise_name = expected_exercise_name.lower() + ext  # TODO: FINALIZE
                expected_exercise_name = getattr(expected_exercise_name, capitalization)()

                expected_exercise = os.path.join(expected_folder, expected_exercise_name)
                if not os.path.isfile(expected_exercise):
                    warning = ("%s is missing the '%s:%s%s' file." % (lastname, project, exercise, ext))
                    warnings.append(warning)

if warnings:
    for warning in warnings:
        logging.warning('\t' + warning)

if not warnings:
    logging.warning("\tALL PROJECTS AND EXERCISES TURNED IN")

if log: logging.warning('')

def main():
    pass


