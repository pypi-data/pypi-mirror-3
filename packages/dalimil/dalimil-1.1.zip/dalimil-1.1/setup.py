from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '1.1'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    "argparse",
    ]

setup(name='dalimil',
    version=version,
    description="Command line tool for organizing files into time related containers (directories or archives)",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      "Development Status :: 4 - Beta",
      "Environment :: Console",
      "Intended Audience :: System Administrators",
      "License :: OSI Approved :: BSD License",
      "Operating System :: Microsoft :: Windows",
      "Operating System :: OS Independent",
      "Operating System :: POSIX :: Linux",
      "Programming Language :: Python :: 2.6",
      "Programming Language :: Python :: 2.7",
      "Topic :: Desktop Environment :: File Managers",
      "Topic :: System :: Archiving :: Backup",
      "Topic :: System :: Archiving :: Compression",
      "Topic :: System :: Archiving :: Packaging",
      "Topic :: Utilities"
    ],
    keywords='archive compress time organize',
    author='Jan Vlcinsky',
    author_email='jan.vlcinsky@gmail.com',
    url='https://bitbucket.org/vlcinsky/dalimil',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=True,
    install_requires=install_requires,
    test_suite="dalimil.tests",
    entry_points={
        'console_scripts':
            ['dalimil=dalimil.dalimil:main']
    }
) 