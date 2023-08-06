import os
from distutils.core import setup
from ccstraps import VERSION

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-ccstraps',
    version=VERSION,
    license='BSD 3 Clause',
    description='A rotating strap application for Django',
    long_description=open('README.rst').read(),
    author='c&c Design Consultants LTD',
    author_email='studio@designcc.co.uk',
    url='https://github.com/designcc/django-ccstraps',
    package_data={
        'ccstraps' : [
            'templates/ccstraps/*.html',
            'static/ccstraps/*.png',
            'static/ccstraps/nivo-slider/*.js',
            'static/ccstraps/nivo-slider/*.txt',
            'static/ccstraps/nivo-slider/*.css',
            'static/ccstraps/nivo-slider/themes/default/*.png',
            'static/ccstraps/nivo-slider/themes/default/*.css',
            'static/ccstraps/nivo-slider/themes/default/*.gif',
        ],
    },
    packages=[
        'ccstraps',
        'ccstraps.templatetags',
        'ccstraps.tests'
    ],
    install_requires=[])
