from distutils.core import setup

setup(
    name='SigmaCommon',
    version='0.1.0',
    author='J. Stephen Sichina',
    author_email='Stephen.Sichina@gmail.com',
    packages=['sigmacommon', 'sigmacommon.test'],
    scripts=['bin/binLaden.py'],
    url='http://pypi.python.org/pypi/SigmaCommon/',
    license='LICENSE.txt',
    description='Hey man whasup?',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)