from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

setup(
    name='uWeb',
    version='0.1.alpha1',
    author='Elmer de Looff',
    author_email='elmer@underdark.nl',
    packages=['uweb',
              'uweb.pagemaker',
              'uweb.ext_lib.underdark',
              'uweb.ext_lib.underdark.libs',
              'uweb.ext_lib.underdark.libs.app',
              'uweb.ext_lib.underdark.libs.app.daemon',
              'uweb.ext_lib.underdark.libs.app.daemon.version',
              'uweb.ext_lib.underdark.libs.app.logging',
              'uweb.ext_lib.underdark.libs.sqltalk',
              'uweb.ext_lib.underdark.libs.sqltalk.mysql',
              'uweb.ext_lib.underdark.libs.sqltalk.sqlite',
              # Demo / example projects
              'uweb.base_project',
              'uweb.base_project.www',
              'uweb.logviewer',
              'uweb.logviewer.router',
              'uweb.uweb_info',
              'uweb.uweb_info.www'],
    package_dir={'uweb.pagemaker': 'uweb/pagemaker',
                 'uweb.base_project': 'uweb/base_project',
                 'uweb.logviewer': 'uweb/logviewer',
                 'uweb.uweb_info': 'uweb/uweb_info'},
    package_data={'uweb.pagemaker': ['http_500.xhtml'],
                  'uweb.base_project': ['templates/*', 'www/*'],
                  'uweb.logviewer': ['static/*'],
                  'uweb.uweb_info': ['templates/*', 'www/*']},
    keywords=['web', 'framework', 'underdark'],
    url='http://uweb-framework.nl/',
    license='ISC',
    description='Underdark\'s minimal Web-framework.',
    long_description=open('README').read(),
    install_requires=[
        "lockfile>=0.9",
        "MySQL-python>=1.2",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
    ]
)
