
'''
setup.py for mikado packages

'''

from distutils.core import setup
import os, glob

def get_version():

    '''return version from fixed always must exist file

       Making very broad assumptions about the 
       existence of files '''
    
    v = open('mikado/oss/doctest_additions/version.txt').read().strip()
    return v




def main():

    setup(name='mikado.oss.doctest_additions',
          version=get_version(),
          packages=['mikado.oss.doctest_additions'
                   ],
          namespace_packages = ['mikado', 'mikado.oss'],
          author='See AUTHORS.txt',
          author_email='info@mikadosoftware.com',
          url='https://github.com/lifeisstillgood/mikado.oss.doctest_additions',
          license='LICENSE.txt',
          description='trivial "patch" to allow doctests to ignore certain lines',
          long_description='see description',
          install_requires=[
              "unittest-xml-reporting",
                           ],
          package_data={'mikado.oss.doctest_additions': ['version.txt', 
                                                         'tests/*.*'],
                        },
          scripts = ['scripts/doctest_additions_runner.py',]

          
          )



if __name__ == '__main__':
    main()

