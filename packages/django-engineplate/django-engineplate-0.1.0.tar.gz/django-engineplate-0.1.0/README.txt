# Setting up.. 

## Register and account on pypi.python.org 
## Share a public key with the website

## then in a folder create a setup.py file
    > In the setup.py file add the following content
         *from distutils.core import setup
         *
         *setup(
         *    name='TowelStuff',
         *    version='0.1.0',
         *    author='J. Random Hacker',
         *    author_email='jrh@example.com',
         *    packages=['towelstuff', 'towelstuff.test'],
         *    scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
         *    url='http://pypi.python.org/pypi/TowelStuff/',
         *    license='LICENSE.txt',
         *    description='Useful towel-related stuff.',
         *    long_description=open('README.txt').read(),
         *    install_requires=[
         *        "Django >= 1.1.1",
         *        "caldav == 0.1.4",
         *    ],
         *)
