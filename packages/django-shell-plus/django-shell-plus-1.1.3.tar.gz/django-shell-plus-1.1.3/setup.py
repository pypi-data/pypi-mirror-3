from distutils.core import setup

setup(
    name = "django-shell-plus",
    version = "1.1.3",
    description = "django-admin.py shell+  <- shell with models auto-imported",
    url = "http://bitbucket.org/schinckel/django-shell+/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "shell_plus",
        'shell_plus.management',
        'shell_plus.management.commands',
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
