from distutils.core import setup

setup(
    name='argpext'
    , version='0.1'
    , description = 'Argpext: Hierarchical argument processing based on argparse.'
    , author='Alexander Shirokov'
    , author_email='alexvso@gmail.com'
    #, packages=['argpext']
    #, scripts = ['argpext.py']
    , py_modules=['argpext']
    , license='OSI Approved'
    , long_description=open('ReadMe.txt').read()
    , classifiers = [
        'Development Status :: 3 - Alpha'
        ,'Environment :: Console'
        ,'Intended Audience :: End Users/Desktop'
        ,'Intended Audience :: Developers'
        ,'Intended Audience :: Information Technology'
        ,'Operating System :: MacOS :: MacOS X'
        ,'Operating System :: Microsoft :: Windows'
        ,'Operating System :: POSIX'
        ,'Programming Language :: Python :: 3'
        ,'Topic :: Office/Business :: Financial'
    ]
)

