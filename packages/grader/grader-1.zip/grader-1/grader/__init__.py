try:
    from os import path
    from time import sleep
    import settings
except ImportError:
    print "ImportError Raised"

if not path.isdir(settings.ROOT):
    settings.setup()
    print "Setting up shop..."

try:
    import grader
except:
    print "Done!"
    print "Next time you call 'grade' you will be able to use it!"
