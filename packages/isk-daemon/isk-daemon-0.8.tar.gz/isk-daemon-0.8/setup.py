#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

# win/linux diffs
import os
# unfortunatelly this is not working
if os.name == 'nt': # fix windows stuff
    imgSeekLib_package_data = ['*.dll']
else: # linux
    imgSeekLib_package_data = ['*.so']
   

with open('README.txt') as file:
    long_description = file.read()

#############################[ Parameters you should change if install failed ]#########################################
# python_dir should point to the directory where Python header files may be found.. (Inside this dir you should have a Python.h)
python_dir="/usr/include/python"
#############################[ End of parameters that can be changed ]##################################################

try:
    import sys,commands,traceback,os
    from distutils import sysconfig
    from distutils.core import setup,Extension
    from distutils.command.build_ext import build_ext
    from distutils.errors import CCompilerError
    from string import *
    import platform
except:
    traceback.print_exc()
    print "Unable to import python distutils."
    print "You may want to install the python-dev package on your distribution."
    sys.exit(1)

############## Init some vars
extra_compile_args=["-O3", "-DLinuxBuild"] #optimize but don't alter semantics
library_dirs = []
include_dirs = []
libraries = []
extra_link_args = []

hasIMagick=0
print "#################################### Check ImageMagick"
try:
    fnd=0
    pathvar=os.environ["PATH"]
    for pv in split(pathvar,':'):
        if os.path.exists(pv+'/Magick++-config') or os.path.exists(pv+'Magick++-config'):
            fnd=1
    if fnd:
        IMagCFlag=os.popen("Magick++-config --cxxflags --cppflags").read()
        if find(IMagCFlag,"-I") != -1:
            IMagCFlag=replace(IMagCFlag,"\n"," ")
            IMagCFlag=split(IMagCFlag,' ')
            IMagCLib=os.popen("Magick++-config --ldflags --libs").read()
            IMagCLib=replace(IMagCLib,"\n"," ")
            IMagCLib=split(IMagCLib,' ')
            hasIMagick=1
    else:
        print "--- WARNING ---\nUnable to find Magick++-config. Are you sure you have ImageMagick and it's development files installed correctly?"
except:
    traceback.print_exc()

if hasIMagick:
    extra_compile_args=extra_compile_args+["-DImMagick"]
    libraries=[]                        # remove all other libraries and only use ImageMAgick
    for cf in IMagCFlag:
        cf=strip(cf)
        if not cf: continue
        extra_compile_args.append(cf)
    for cf in IMagCLib:
        cf=strip(cf)
        if not cf: continue
        extra_link_args.append(cf)
    print "Found the following arguments:"
    print "extra_compile_args",extra_compile_args
    print "extra_link_args",extra_link_args
else:
    print "ImageMagick library and development files not found."

print "Checked."

class fallible_build_ext(build_ext):
    """the purpose of this class is to know when a compile error ocurred """
    def run(self):
        try:
            build_ext.run(self)
        except CCompilerError:
            traceback.print_exc()


# force C++ linking
from distutils import sysconfig
config_vars = sysconfig.get_config_vars()
for k, v in config_vars.items():
    if k.count('LD') and str(v).startswith('gcc'):
        print "+++++++++++++++++++++++++++++++++++++++++++++"
        config_vars[k] = v.replace('gcc', 'g++')

            
print "#################################### Installing"
setup(name="isk-daemon",
      version='0.8',
      description="Server and library for adding content-based (visual) image searching to any image related website or software.",
      long_description=long_description,
      keywords = "imgseek iskdaemon image cbir imagedatabase isk-daemon database searchengine",
      author="Ricardo Niederberger Cabral",
      author_email="ricardo.cabral at imgseek.net",
      url="http://server.imgseek.net/",
      download_url = "http://www.imgseek.net/isk-daemon/download",
      platforms = ['Linux','Windows','Mac OSX'],
      cmdclass = { 'build_ext': fallible_build_ext},
      ext_modules = [
        Extension("imgdb",["imgSeekLib/imgdb.cpp",
                           "imgSeekLib/haar.cpp",
                           "imgSeekLib/bloom_filter.cpp"
                                      ],
                  include_dirs = include_dirs,
                  library_dirs = library_dirs,
                  extra_compile_args=extra_compile_args,
                  extra_link_args=extra_link_args,
                  libraries = libraries,
                  swig_opts = ['-c++']
                 )],
      license = 'GPLv2',
      packages=['imgSeekLib'],
      #package_data={'imgSeekLib': imgSeekLib_package_data},
      scripts= ['isk-daemon.py','default_settings.py','settings.py'],
      install_requires = ['Twisted >= 8',
                          'simplejson',
                          'fpconst',
                          'SOAPpy == 0.11',
                          ],
      dependency_links = ["http://sourceforge.net/project/showfiles.php?group_id=26590&package_id=18246",
                         ],
     )
