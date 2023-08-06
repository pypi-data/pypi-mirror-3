import os
import sys
import subprocess
from setuptools import setup


if not os.path.exists('builtfsources'):
    print "Trying to build Fortran Sources with f90 installer..."
    fbuild = subprocess.Popen('make', cwd='fsource', shell=True)
    fbuild.wait()
    if fbuild.returncode != 0:
        print "Failed with f90; trying ifort..."
        ifbuild = subprocess.Popen('make FC=ifort', cwd='fsource', shell=True)
        ifbuild.wait()
        sys.exit(0)
        if ifbuild.returncode != 0:
            print "FAIL: Couldn't build fortran sources with f90 or ifort."
            sys.exit(0)
    print "Success."
    done = open('builtfsources', 'w')
    done.write('yep')
    done.close()

readme = open('README.txt').read()
setup(
    name='PySBdart',
    version='0.0.3',
    author='Philip Schleihauf',
    author_email='uniphil@gmail.com',
    license='Public Domain', #????
    description='Numerical Computations',
    long_description=readme,
    #url='https://github.com/uniphil/FMM',
    py_modules=['sbdart'],
    data_files=[
        ('test_outs', [
            'sbouts/sbout.1',
            'sbouts/sbout.2',
            'sbouts/sbout.3',
            'sbouts/sbout.4',
            'sbouts/sbout.5',
            ]),
        ('fsource', [
            'fsource/atms.f',
            'fsource/disort.f',
            'fsource/disutil.f',
            'fsource/drt.f',
            'fsource/Makefile',
            'fsource/params.f',
            'fsource/spectra.f',
            'fsource/tauaero.f',
            'fsource/taucloud.f',
            'fsource/taugas.f',
            ]),
        ],
    scripts=['fsource/sbdart'],
    )
