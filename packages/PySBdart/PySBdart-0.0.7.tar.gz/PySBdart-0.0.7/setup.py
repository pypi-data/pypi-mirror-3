

from setuptools import setup, command

class CompileAndInstall(command.install.install):
    def run(self):
        import subprocess
        fcompilers = ['f90', 'ifort', 'pgfortran']
        for fc in fcompilers:
            fbuild = subprocess.Popen('make FC=%s' % fc,
                                      cwd='fsource', shell=True)
            fbuild.wait()
            print "RETURN CODE FOR %s: %d" % (fc, fbuild.returncode)
            if fbuild.returncode == 0:
                break
            if fc is fcompilers[-1]:
                print "FAIL: Couldn't build fortran sources."
                import sys
                sys.exit(0)
        
        command.install.install.run(self)


readme = open('README.txt').read()
setup(
    name='PySBdart',
    version='0.0.7',
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
    cmdclass={'install': CompileAndInstall},
    )
    
    
