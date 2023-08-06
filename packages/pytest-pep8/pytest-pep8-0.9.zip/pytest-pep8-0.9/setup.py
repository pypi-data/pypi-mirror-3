from setuptools import setup
setup(
    name='pytest-pep8',
    description='pytest plugin to check source code against PEP8 requirements',
    long_description=open("README.txt").read(),
    version='0.9',
    author='Holger Krekel and Ronny Pfannschmidt',
    author_email='holger.krekel@gmail.com',
    url='http://bitbucket.org/hpk42/pytest-pep8/',
    py_modules=['pytest_pep8'],
    entry_points={'pytest11': ['pep8 = pytest_pep8']},
    install_requires=['pytest>=2.0', 'pep8>=1.3', ],
)
