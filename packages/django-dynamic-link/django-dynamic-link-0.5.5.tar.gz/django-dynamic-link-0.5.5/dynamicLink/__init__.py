import version
import os
import django
import sys

__version__ = VERSION = version.VERSION
RELEASE_DJANGO = version.RELEASE_DJANGO

try:
    __doc__ = open(os.path.join(os.path.dirname(__file__), 'README_COPY')).read()
    __docformat__ = 'reStructuredText'
except IOError:
    __doc__ = 'For full documentation review the README file in your package or go to:' \
    'http://pypi.python.org/pypi/django-dynamic-link/'
    __docformat__ = 'txt'

def CKINST():
    """function to find problems of the installation."""
    print('I try to find errors for you!')
    
    djv = django.VERSION[:2]
    greatest_dlv = version.RELEASE_DJANGO[0]
    smalest_dlv = version.RELEASE_DJANGO[0]

    def strform(val):
        """returns formated version tuples"""
        return str(val).strip('()').replace(' ', '').replace(',','.')

    # find greatest and smallest possible django version for dynamic link
    for dlv in version.RELEASE_DJANGO:
        if greatest_dlv < dlv:
            greatest_dlv = dlv
        if smalest_dlv > dlv:
            smalest_dlv = dlv

    # check dynaic link dependences
    if djv < smalest_dlv:
        print('Error! Django %s is not supported. With the installed version of dynamicLink is Django %s recommended. ' \
        'Use "pip install django==%s.X". ' \
        'To display all supported django versions use "dynamicLink.RELEASE_DJANGO".' \
        % (str(django.VERSION), strform(greatest_dlv), strform(greatest_dlv) ))
    elif djv > greatest_dlv:
        print('Error! This Version of dynamicLink (try: "dynamicLink.VERSION") needs an ' \
        'older Django release (try: "dynamicLink.RELEASE_DJANGO"). ' \
        'Use "pip install --upgrade django-dynamic-link" or use "pip install django==%s.X". '\
        % strform(greatest_dlv))
    elif sys.version_info[:2] < version.PYTHON_MIN:
        print('Error! Wrong python version. dynamicLink depends on python %s or higher. ' \
        'With this python installation dynamicLink will not work properly!' \
        % strform(version.PYTHON_MIN))
    else:
        print("No errors. All seems fine!")

