#!/usr/bin/env python
from distutils.core import setup
import os


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)


def package_files(package_name):
    """
    Build a list of data files contained within a module
    """
    data_files = []

    for dirpath, dirnames, filenames in os.walk(package_name):
        if '__init__.py' not in filenames:
            dir_name = os.sep.join(fullsplit(dirpath)[1:])
            data_files.extend([os.path.join(dir_name, f) for f in filenames])

    return data_files


setup(
    name='django-tinymce-staticfiles',
    version='3.4.7',
    description='TinyMCE Static Files for Django',
    long_description=open('README.rst').read(),
    url='http://www.tinymce.com/',
    maintainer='Alex Tomkins',
    maintainer_email='alex@hawkz.com',
    platforms=['any'],
    packages=[
        'tinymce_staticfiles',
    ],
    package_data={
        'tinymce_staticfiles': package_files('tinymce_staticfiles'),
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    license='LGPL',
)
