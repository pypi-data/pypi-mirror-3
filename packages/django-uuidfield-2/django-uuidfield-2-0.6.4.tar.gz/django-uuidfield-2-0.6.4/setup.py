from distutils.core import setup

setup(
    name = "django-uuidfield-2",
    version = "0.6.4",
    description = "UUIDField for django models",
    url = "http://bitbucket.org/schinckel/django-uuidfield/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "uuidfield",
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
