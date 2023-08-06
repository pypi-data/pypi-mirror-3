Grader
******

Grader is a custom assignment checker for a 3D modeling class, but it is flexible enough that it could be useful for some other purpose.
Written by Luis Naranjo

**Usage**

When grader is run for the first time it creates a folder called 'grader' in My Documents (Windows) or Documents (Mac).

Here are the contents of 'grader':

settings.conf

students.txt

grader_files\

log.txt

settings.conf
*************

Settings
========

This file is where the projects are defined.

The file starts out with the following program settings:

**show members**

This controls whether the contents of a student's missing project are to be reported missing or not.

It can be either True or False

For example::

   show members = True

Putting this in settings.conf would make the grader report each missing file within a missing project.

If it were set to false, the grader would only report that the project is missing.

**capitalization**

This controls the capitalization of the student projects.

The grader relies on the consistency of the project/exercise naming.

Students are not the most reliable for correct formatting, so grader includes a way to normalize all of the files/folders in the grader_files folder.

capitalization has the following possible values: capitalize, lower, upper, title

capitalize only capitalizes the first word.

lower makes everything lower case.

upper makes everything upper case.

title capitalizes every word.

For example::

   capitalization = lower

This would make every folder and file in the grader_files folder lowercase.

Note:

* Watch out for upper and title, they can mess up your file extensions.
* If you don't set this correctly, grader won't function.

**log**

This controls where grader's results are reported.

It can be either True or False

If it is True, the results are recorded in My Documents/grader/log.txt

If it is False, the results are printed to the command line and not saved.

Projects
========

You can define as many projects as you want

Each project can have as many exercises as you want.

Each exercise can have as many file extensions as you want.

For example::

   [project 3]
   exercise 1 = .jpg,.3dm
   exercise 2 = .3dm

Notice that exercise 1 has two file extensions, and they are separated by commas, not spaces.

If we only had one student (naranjo) defined in students.txt, grader would look for the following files and folders in grader_files\\:

naranjo project 3\\ (folder)

naranjo exercise 1.jpg (inside of naranjo project 3)

naranjo exercise 1.3dm (inside of naranjo project 3)

naranjo exercise 2.3dm (inside of naranjo project 3)

students.txt
************

This is where the students are defined.

students.txt is very simple.

Each line in the file should have the last name of the student, and nothing more.

Do not skip any lines.

This will work::

   depp
   clooney
   naranjo

This will not::

   depp

   clooney

   naranjo

grader_files
************

This is the folder where you put the student projects.
Each folder should be named according to the following convention (things enclosed by brackets are variables):

{lastname} {projectname}

The exercises contained in these folders should match the following convention:

{lastname} {exercisename}

log.txt
*******

Results can be stored here.

This is controlled via the log variable in settings.conf


Installation
************

Grader is written in python2.7.3, so python must be installed before it can be run.

There is a great guide on how to install here: http://docs.python-guide.org/en/latest/index.html

It has only one dependency (configobj), which is bundled with the program.

It is available on the python package index at http://pypi.python.org/pypi/grader

Source code is up on https://github.com/doubledubba/grader

Once it is installed, grader sets up a console script called 'grader'.

This allows you to open the command prompt/terminal and type 'grader' and hit enter.

This should activate grader.

What you would see on the command prompt depends on what you set your log variable as in settings.config

Grader also adds a batch file (grader.bat) which automates this process for clicking.

If you are on Windows, you should be able to click this to run grader.

A similar file is created for Linux and Mac operating systems called grader.sh
