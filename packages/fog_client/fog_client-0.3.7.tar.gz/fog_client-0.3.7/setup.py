from setuptools import setup, find_packages
import os
import glob

datadir = 'aux'
datafiles = [(datadir, [f for f in glob.glob(os.path.join(datadir, '*'))])]


setup(
    name='fog_client',
    version='0.3.7',

    author='Carles Gonzalez',
    packages=find_packages(),
    py_modules=['fog_lib', 'fog_client'],
    install_requires=['cuisine', 'requests>=0.13'],
    scripts=['fog_client.py'],
    data_files=datafiles,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration'])
