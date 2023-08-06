from setuptools import setup, find_packages
import os

version = '0.0.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'i18n', 'test_i18n.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.i18n',
    version=version,
    description="fanstatic i18n-js bundle",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Moriyoshi Koizumi',
    author_email='mozo@mozo.jp',
    license='MIT',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        ],
    entry_points={
        'fanstatic.libraries': [
            'i18n = js.i18n:library',
            ],
        #'console_scripts': [
        #    'download_jqueryui = js.jqueryui.download:main'],
        },
    )
