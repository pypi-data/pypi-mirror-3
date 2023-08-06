from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.3'
install_requires = []

if sys.version_info < (2,7):
    installrequires.append('argparse')
elif sys.version_info >= (3,0) and sys.version_info < (3,2):
    install_requires.append('argparse')

tests_require = [
    'nose',
    'ipdb',
    'distribute',
]

setup(name='lpjsmin',
    version=version,
    description="JS Min script that provides cmd line and python processors",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='javascript minification compress',
    author='Rick Harding',
    author_email='rharding@canonical.com',
    url='https://launchpad.net/lpjsmin',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points={
        'console_scripts':
            ['lpjsmin=lpjsmin:main']
    }
)
