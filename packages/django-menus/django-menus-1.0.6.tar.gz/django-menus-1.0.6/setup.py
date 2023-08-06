from distutils.core import setup

# Not sure of a better way to automatically generate this file.
# It needs to happen before setup() is called to ensure that
# long_description is set.
try:
    import subprocess
    subprocess.call(["pandoc", "README.md", '-t', 'rst', '-o', 'README.rst'])
except (OSError, IOError):
    pass
        
setup(
    name = "django-menus",
    version = "1.0.6",
    description = "Menu helpers for django projects",
    url = "http://bitbucket.org/schinckel/django-menus/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "menus",
        "menus.templatetags"
    ],
    package_data = {
        "menus": [
            "static/menus/*/*",
            "templates/menu/*",
        ],
    },
    long_description = open("README.rst").read(),
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
