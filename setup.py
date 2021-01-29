"""setuptools file for the package."""
import os

from setuptools import find_packages
from setuptools import setup

PACKAGE_NAME = "plex_remote_transcoder"

EXTRAS = {
    'dev-tools': ['flake8',
                  'flake8-bugbear',
                  'flake8-builtins',
                  'flake8-comprehensions',
                  'flake8-docstrings',
                  'flake8-eradicate',
                  'flake8-expression-complexity',
                  'flake8-import-order',
                  'flake8-import-single',
                  'flake8-print',
                  'flake8-return',
                  'pep8-naming']
}

with open("VERSION", "r") as versionFile:
    version = versionFile.read().strip()

with open(os.path.join(PACKAGE_NAME, "__version__.py"), "w") as versionFile:
    versionFile.write('"""Auto-generated version file."""\n')
    versionFile.write('VERSION = "{}"'.format(version))

setup(
    name=PACKAGE_NAME,
    version=version,
    description='A remote transcoder for Plex (Python3)',
    url='https://github.com/TheFrisbeeNinja/Plex-Remote-Transcoder',
    author='Kenji Ryan Yamamoto',
    author_email='TheFrisbeeNinja@github',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='plex media server, distributed plex, load balancing, remote transcoding',
    py_modules=find_packages(),
    entry_points={
        'console_scripts': [
            'prt3=plex_remote_transcoder.main:main',
            'prt3-remote=plex_remote_transcoder.remote:main'
        ],
    },
    install_requires=['termcolor', 'psutil', 'pbr', 'asyncio', 'requests', 'lxml'],
    extras_require=EXTRAS
)
