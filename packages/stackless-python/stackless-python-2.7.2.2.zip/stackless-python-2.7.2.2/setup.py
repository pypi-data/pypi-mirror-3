from distutils.core import setup
from distutils.util import get_platform
from distutils.command.install_data import install_data
from distutils import log


import sys
from os.path import join, dirname, abspath
from os import remove

from zipfile import PyZipFile

stacklessVersion = (2,7,2)
installerVersion = (2,)

stacklessVersionStr = ".".join(map(str,stacklessVersion))
installerVersionStr = ".".join(map(str,stacklessVersion + installerVersion))

if sys.version_info[:3] not in ((2, 7, 2), (2,7,3)):
    print 'ERROR: Stackless Python %s requires Python %s to run.' % (stacklessVersionStr, stacklessVersionStr)
    sys.exit(1)


pyAndVersion="python" + str(stacklessVersion[0]) + str(stacklessVersion[1])

platform = get_platform()
distRoot = dirname(__file__)

data_files=[]
cmdclass = {}

if "win32" == platform:
    arch="win32"
    assembly="com.stackless."+pyAndVersion
    zipName=pyAndVersion + ".zip"
    zipSrc="Lib"
    fullZipName = join(distRoot, zipName)

    pylib = [join(arch, assembly, assembly+".MANIFEST"),
             join(arch, assembly, pyAndVersion+".dll"),
             zipName]
    pyexe = [join(arch, 'slpython.exe'), join(arch,'slpythonw.exe')]
    
    pybindest = ''
    pylibdest = assembly


    class my_install_data(install_data):
        def run(self):
            try:
                remove(fullZipName)
            except OSError, e:
                pass
                # print >> sys.stderr, "Failed to remove %s: %s" % (fullZipName, e)
            with PyZipFile(fullZipName, 'w') as myzip:
                log.info("creating library archiv %s", fullZipName)
                # myzip.debug = True
                myzip.writepy(join(distRoot, zipSrc))
                myzip.writepy(join(distRoot, zipSrc, "distutils"))
            try:
                install_data.run(self)
            finally:
                try:
                    log.info("removing library archiv %s", fullZipName)
                    remove(fullZipName)
                except OSError, e:
                    log.error("faild to remove library archiv %s: %s", fullZipName, e)
                    pass

    cmdclass['install_data'] = my_install_data


else:
    raise NotImplementedError("Platform %s not yet supported" % (platform,))
       
data_files.extend([(pybindest, pyexe),
                   (pylibdest, pylib )])

setup(
    cmdclass=cmdclass,
    name='stackless-python',
    version=installerVersionStr,
    description='Installer for Stackless Python',
    author='Christian Tismer',
    author_email='tismer@stackless.com',
    maintainer='Anselm Kruis',
    maintainer_email='a.kruis@science-computing.de',
    url='http://www.stackless.com',
    packages=[],
    data_files=data_files, 
    long_description=
"""
Installer for Stackless Python
------------------------------

This installer adds two additional executables slpython.exe and slpythonw.exe
to your Python installation. It does not compromise your regular CPython installation.

Sorry, currently only for Python 2.7.2 on win32.

Git repository: coming soon
""",
    classifiers=[
          "License :: OSI Approved :: Python Software Foundation License",
          "Programming Language :: Python",
          "Programming Language :: Python :: "+".".join(map(str,stacklessVersion[:2])),
          "Programming Language :: Python :: Implementation :: Stackless", 
          "Environment :: Win32 (MS Windows)",
          "Operating System :: Microsoft :: Windows :: Windows XP",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='stackless',
      license='Python Software Foundation License',
      platforms="win32",
    )
