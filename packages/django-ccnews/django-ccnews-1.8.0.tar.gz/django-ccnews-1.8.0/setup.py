import os
from distutils.core import setup
from ccnews import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-ccnews',
    version=get_version(),
    license='BSD 3 Clause',
    description='A lightweight news application for Django',
    long_description=open('README.rst').read(),
    author='c&c',
    author_email='studio@designcc.co.uk',
    url='https://github.com/designcc/django-ccnews',
    package_data={
        'ccnews' : [
            'templates/ccnews/*.html',
            'templates/search/indexes/ccnews/*.txt',
            'static/ccnews/css/*.css',
            'static/ccnews/test.pdf',
            'static/ccnews/fancybox/source/*.gif',
            'static/ccnews/fancybox/source/*.png',
            'static/ccnews/fancybox/source/*.css',
            'static/ccnews/fancybox/source/*.js',
            'static/ccnews/fancybox/source/*.png',
            'static/ccnews/fancybox/source/helpers/*.png',
            'static/ccnews/fancybox/source/helpers/*.css',
            'static/ccnews/fancybox/source/helpers/*.js',
        ],
    },
    packages=[
        'ccnews',
        'ccnews.templatetags',
        'ccnews.tests'
    ],
    install_requires=[
        'django-ccthumbs',
        'django-writingfield',
        'django-ccfiletypes',
       'markdown2'])
