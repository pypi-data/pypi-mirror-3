from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n\n'
    + read('CHANGES.txt')
    + '\n\n'
    + 'Download\n'
    + '********\n'
    )

setup(
    name='ulif.loghandlers',
    version='0.1',
    author='Uli Fouquet',
    author_email='uli@gnufix.de',
    url = 'http://pypi.python.org/pypi/ulif.loghandlers',
    description='Additional logging handlers.',
    long_description=long_description,
    license='LGPL',
    keywords="logging logger rotating",
    classifiers=['Development Status :: 3 - Alpha',
                 'Framework :: Buildout',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: System :: Logging',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['ulif'],
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'zc.buildout',
                      ],
    setup_requires=['Sphinx-PyPI-upload',
                    ],
    extras_require=dict(
        test = ['pytest',
                'pytest-xdist',
                'pytest-cov',
                ],
        ),
    entry_points="""
    [console_scripts]
      """,
)
