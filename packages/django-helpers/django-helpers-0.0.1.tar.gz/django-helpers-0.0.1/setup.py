__author__ = 'ajumell'
from distutils.core import setup
import os

CUR_DIR = os.path.dirname(__file__)
CODE_DIR = os.path.join(CUR_DIR, "django_helpers")
EXCLUDED_DIRECTORIES = ["templates", "static"]
ADDITIONAL_DIRECTORIES = ["templates", "static"]
SCRIPTS = []
ADDITIONAL_FILES = []

def is_excluded(name):
    for d in EXCLUDED_DIRECTORIES:
        d = "django_helpers/" + d
        print d, name
        if name.startswith(d):
            return True
    return False

for r, d, f in os.walk(CODE_DIR):
    for files in d:
        package = os.path.join(r, files)
        if not is_excluded(package):
            package = package.replace("/", ".")
            SCRIPTS.append(package)
print SCRIPTS

for d in ADDITIONAL_DIRECTORIES:
    dir_files = []
    for r, d, f in os.walk(os.path.join(CODE_DIR, d)):
        for files in f:
            dir_files.append(os.path.join(r, files))
    ADDITIONAL_FILES.append((d, dir_files))

setup(
    name='django-helpers',
    version='0.0.1',
    long_description='',
    description='Django Helpers and form addons.',
    author='Muhammed K K',
    author_email='ajumell@gmail.com',
    url="http://www.xeoscript.com/",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ],
    data_files=ADDITIONAL_FILES,
    platforms=["any"],
    license="Freely Distributable",
    packages=SCRIPTS,
    install_requires=[
        "Django >= 1.4"
    ]
)
