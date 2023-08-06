Grader is an assignment completion checker written in python.

After installation, it sets itself up in your Documents, in a folder called grader.

Here is the folder structure:

GRADER\
    GRADER.BAT (This is what runs the program - It writes the results of the diagnostics to log.txt)
    GRADER_SETTINGS.CONF (Defines the project names and required exercises)
    STUDENTS.TXT (Registry of students)
    LOG.TXT (after grader.bat has been run)
    STUDENT_FILES\
        naranjo project 3 (example project)

In the grader folder, there is a folder called 'student_files'.

This is where the students' project folders are supposed to go.
Make sure not to just empty the files there - they have to be folders.
They have to follow the following syntax "lastname projectname"

lastname is defined in the students.txt file.
The students.txt file is the student registry that grader uses.
Each line represents a student.
The first value is the students' first name.
The second value is the students' last name.
The third value is the students' class period.
Note that each value is separated by a space.

projectname is defined in the "grader_settings.conf" file.
You can edit this with notepad, but not MS Word.
The syntax is pretty clear. The project name is denoted by brackets.
Below the project name, add "docs = file1, file2" etc...

If you have doubts with any of the configuration files, open them and look at them.
I've written some defaults that you can easily reverse-engineer to your purposes.
Let me know if you have any questions
    -Luis

