#!/usr/bin/env python

from distutils.core import setup

setup(
    name='smtpdropbox',
    version='1.0',
    description='Pure-python library to capture emails into a dropbox',
    author='Kevin J. Rice',
    author_email='justanyone@gmail.com',
    maintainer='Kevin J. Rice',
    maintainer_email='justanyone@gmail.com',
    packages=[''],
    py_modules = ['smtpdropbox'],
    url="http://pypi.python.org/pypi/smtpdropbox/1.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Office/Business',
        ],
    long_description="""
Readme File for smtpdropbox

Smtpdropbox is a subclass of the smtpd module.  It allows a user
to set up an smtp daemon on a random port and send emails to it.
When the daemon receives an email, it parses it and saves the
parsed data structure to a file on the filesystem.  This file is
saved in JSON format (using the standard JSON library of Python)
to help users easily recreate / use the data from the email.

Common uses for this module are for testing software that sends
automated emails.  If that software points to this smtp server,
the emails can be trapped and parsed automatically, verifying that
the email was sent and what is in the email.

FUTURE WORK

This library does not save file attachments (yet).  An enhancement
would be to make it save any/all attachments as individual files,
hopefully named the same as they were in the email.

Also, future work includes adding the ability to save the mail
message received as a plain text file as well as a json file.  it
currently does not do so, though it hasn't been done yet.


PARAMETERS

When instantiating this class, you specify the boxname (really, this
is localhost or 127.0.0.1) and port number to listen on, the
boxname to forward messages to (as yet unimplemented), the names of
the textfile and json file, and the number of messages to process
before exiting (0=infinite).


The test has a complete example of usage.
"""
     )


