import os

from setuptools import setup, find_packages


classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Utilities
Operating System :: Unix
"""

def read(*rel_names):
    return open(os.path.join(os.path.dirname(__file__), *rel_names)).read()


setup(
    name='crammit',
    version='0.2',
    url='https://github.com/rspivak/crammit.git',
    license='MIT',
    description=('Asset packaging library. '
                 'Concatenates, Minifies, and Compresses CSS and JavaScript'),
    author='Ruslan Spivak',
    author_email='ruslan.spivak@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['slimit', 'cssmin', 'PyYAML'],
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    crammit = crammit:main
    """,
    classifiers=filter(None, classifiers.split('\n')),
    long_description=read('README.rst') + '\n\n' + read('CHANGES.rst'),
    extras_require={'test': []}
    )
