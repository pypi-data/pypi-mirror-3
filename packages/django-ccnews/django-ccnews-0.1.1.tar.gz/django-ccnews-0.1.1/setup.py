import os
from distutils.core import setup
from ccnews import VERSION

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-ccnews',
    version=VERSION,
    license='BSD 3 Clause',
    description='A lightweight news application for Django',
    long_description=open('README.rst').read(),
    author='c&c',
    author_email='studio@designcc.co.uk',
    url='https://github.com/designcc/django-ccnews',
    package_data={
        'ccnews' : [
            'templates/ccnews/*.html',
            'static/ccnews/css/*.css',
            'static/ccnews/test.pdf',
        ],
    },
    packages=[
        'ccnews',
        'ccnews.templatetags',
        'ccnews.tests'
    ],
    install_requires=[
        'django-ccthumbs',
        'django-ccfiletypes',
       'markdown'])
