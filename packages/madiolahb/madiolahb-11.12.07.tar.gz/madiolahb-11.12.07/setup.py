#!/usr/bin/python
from setuptools import setup

setup(
    name='madiolahb',
    version='11.12.07',
    description='madiolahb -- Bahloidam laboratory',
    author='Max Battcher',
    author_email='me@worldmaker.net',
    url='http://madiolahb.code.worldmaker.net',
    packages=['madiolahb'],
    entry_points={
        'console_scripts': [
            'madiolahb = madiolahb.__main__:main',
        ],
    },
    install_requires=[
        'argparse',
    ],
    license='Microsoft Reciprocal License (Ms-RL)',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
    ],
    zip_safe=True,
)

# vim: ai et ts=4 sts=4 sw=4
