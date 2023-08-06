from setuptools import setup, find_packages
import os

version = '0.0.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jqueryui_bootstrap', 'test_jqueryui_bootstrap.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jqueryui_bootstrap',
    version=version,
    description="fanstatic jQuery UI bootstrap theme.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Moriyoshi Koizumi',
    author_email='mozo@mozo.jp',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jqueryui',
        ],
    entry_points={
        'fanstatic.libraries': [
            'jqueryui_bootstrap = js.jqueryui_bootstrap:library',
            ],
        #'console_scripts': [
        #    'download_jqueryui = js.jqueryui.download:main'],
        },
    #extras_require={
    #    'scripts': [
    #        'lxml',
    #    ],
    #}
    )
