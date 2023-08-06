from distutils.core import setup

import filtered_form

setup(
    name = "django-filtered-form",
    version = filtered_form.__version__,
    description = "A Form that can have per-field queryset filters declaratively defined",
    long_description = open('README.txt').read(),
    url = "http://bitbucket.org/schinckel/django-filtered-form",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "filtered_form",
    ],
    package_data = {
        '': ['VERSION']
    },
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
    ],
)

