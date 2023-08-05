from distutils.core import setup

setup(
    name = "django-menus",
    version = "1.0",
    description = "Menu helpers for django projects",
    url = "http://bitbucket.org/schinckel/django-menus/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "menus",
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
