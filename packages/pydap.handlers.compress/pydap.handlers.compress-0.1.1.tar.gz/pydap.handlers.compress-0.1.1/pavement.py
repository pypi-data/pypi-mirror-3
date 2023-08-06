import string

from paver.easy import *
from paver.setuputils import *
import paver.doctools
from paver.release import setup_meta

__version__ = (0,1,1)

options = environment.options
setup(**setup_meta)

options(
    setup=Bunch(
        name='pydap.handlers.compress',
        version='.'.join(str(d) for d in __version__),
        description='compress handler for Pydap',
        long_description='''
Pydap is an implementation of the Opendap/DODS protocol, written from
scratch. This handler enables Pydap to serve compressed NetCDF files on
the network for Opendap clients.
        ''',
        keywords='netcdf compress opendap dods dap data science climate oceanography meteorology',
        classifiers=filter(None, map(string.strip, '''
            Development Status :: 5 - Production/Stable
            Environment :: Console
            Environment :: Web Environment
            Framework :: Paste
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: MIT License
            Operating System :: OS Independent
            Programming Language :: Python
            Topic :: Internet
            Topic :: Internet :: WWW/HTTP :: WSGI
            Topic :: Scientific/Engineering
            Topic :: Software Development :: Libraries :: Python Modules
        '''.split('\n'))),
        author='Nicholas Lederer',
        author_email='lederer@apl.washington.edu',
        url='http://pydap.org/handlers.html#compress',
        license='MIT',

        packages=find_packages(),
        package_data=find_package_data("pydap", package="pydap",
                only_in_packages=False),
        include_package_data=True,
        zip_safe=False,
        namespace_packages=['pydap', 'pydap.handlers'],

        test_suite='nose.collector',

        dependency_links=[],
        install_requires=[
            'Pydap',
            'pupynere>=1.0.8',
        ],
        entry_points="""
            [pydap.handler]
            compress = pydap.handlers.compress:Handler
        """,
    ),
    minilib=Bunch(
        extra_files=['doctools', 'virtual']
    ),
)


@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass

