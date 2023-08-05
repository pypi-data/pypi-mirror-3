from __future__ import with_statement
from setuptools import setup, find_packages

version_classifiers = ['Programming Language :: Python :: %s' % version
                       for version in ['2', '2.5', '2.6', '2.7']]
other_classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers',
    'Environment :: Console',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Testing',
    ]

with open('README', 'rt') as file_obj:
    detailed_description = file_obj.read()
with open('CHANGELOG', 'rt') as file_obj:
    detailed_description += file_obj.read()

setup(
    name="nosy",
    version="1.1.2",
    description="""\
Run the nose test discovery and execution tool whenever a source file
is changed.
    """,
    long_description=detailed_description,
    author="Doug Latornell",
    author_email="djl@douglatornell.ca",
    url="http://douglatornell.ca/software/python/Nosy/",
    license="New BSD License",
    classifiers=version_classifiers + other_classifiers,
    packages=find_packages(),
    entry_points={'console_scripts':['nosy = nosy.nosy:main']}
)
