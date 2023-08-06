from setuptools import setup
import auth_additions

setup(
    name = "django-auth-additions",
    version = auth_additions.__version__,
    description = "Additions (monkey-patches) to auth models.",
    long_description = open("README.rst").read(),
    url = "http://bitbucket.org/schinckel/django-auth-additions",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "auth_additions",
    ],
    include_package_data = True,
    package_data = {
        '': ['VERSION']
    },
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
