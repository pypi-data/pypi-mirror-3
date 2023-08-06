import os
from distutils.core import setup
from ccsitemaps import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-ccsitemaps',
    version=get_version(),
    license='BSD 3 Clause',
    description='A static sitemap generator for Django',
    long_description=open('README.rst').read(),
    author='c&c Design Consultants LTD',
    author_email='studio@designcc.co.uk',
    url='https://github.com/designcc/django-ccsitemaps',
    package_data={
        'ccsitemaps' : [
            'templates/ccsitemaps/*.xml',
        ],
    },
    packages=[
        'ccsitemaps',
        'ccsitemaps.tests',
        'ccsitemaps.management.commands',
        'ccsitemaps.management',
    ],
    install_requires=[])
