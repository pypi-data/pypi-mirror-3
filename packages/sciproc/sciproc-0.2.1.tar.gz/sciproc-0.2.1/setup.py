from distutils.core import setup

setup(
    name='sciproc',
    version='0.2.1',
    author='H. Wouters',
    author_email='hendrik.wouters@gmail.com',
    packages=['sciproc'],
    #scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://www.nowebsite.com',
    license='LICENSE.txt',
    description='Process scientific data.',
    long_description=open('README.txt').read(),
)
