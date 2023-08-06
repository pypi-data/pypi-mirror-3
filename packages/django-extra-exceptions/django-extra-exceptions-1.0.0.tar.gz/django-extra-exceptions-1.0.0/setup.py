from os.path import join, dirname
from distutils.core import setup

try:
    f = open(join(dirname(__file__), 'README.rst'))
    long_description = f.read().strip()
    f.close()
except IOError:
    long_description = None

setup(
    name='django-extra-exceptions',
    version='1.0.0',
    url="https://github.com/chronossc/http403",
    description='Extra exception handling to mirror django.http.http404',
    long_description=long_description,
    author='Philipe',
    author_email='philipe.rp@gmail.com',
    license='LICENSE',
    keywords='django exceptions http403'.split(),
    platforms='any',
    packages=['extra_exceptions',],
    install_requires=[
        "Django >= 1.3",
    ],
    package_data={'extra_exceptions': [
        'templates/extra_exceptions/default_error_page.html',
    ]},
)
