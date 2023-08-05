from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.2.5'

install_requires = [
    "mako==0.5.0",
    "argparse"
]


setup(name='tacot',
    version=version,
    description="With Tacot generate easily your statics web sites",
    long_description=README + '\n\n' + NEWS,
    keywords='',
    author='Stephane Klein',
    author_email='stephane@harobed.org',
    url='http://packages.python.org/tacot/',
    license='MIT License',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['tacot=tacot:main']
    }
)
