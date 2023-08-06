from distutils.core import setup
import admin_additions

setup(
    name = "django-admin-additions",
    version = admin_additions.__version__,
    description = "Admin additions.",
    long_description = open('README.rst').read(),
    url = "http://hg.schinckel.net/django-admin-additions",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "admin_additions",
    ],
    classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)

