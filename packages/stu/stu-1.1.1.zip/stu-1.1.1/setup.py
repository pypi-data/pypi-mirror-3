try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
    name = "stu",
    version = "1.1.1",
    author = "Jose Luis Naranjo Gomez",
    author_email = "luisnaranjo733@hotmail.com",
    description = ("A simple python template creator."),
    license = "GNU GPLv3",
    scripts = ['stu.py'],
    install_requires='argparse',
    entry_points = {
    'console_scripts': ['stu = stu:main']
    },
    package_data = {'': ['*.txt']},
    keywords = "stu quick python script creator with personalized message",
    long_description=read('README.txt'),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Utilities",
    ],
)
    
