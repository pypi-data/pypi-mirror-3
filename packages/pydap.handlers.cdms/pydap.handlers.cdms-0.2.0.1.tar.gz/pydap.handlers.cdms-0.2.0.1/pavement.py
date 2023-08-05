import string

from paver.easy import *
from paver.setuputils import *
import paver.doctools
from paver.release import setup_meta

__version__ = (0,2,0,1)

options = environment.options
setup(**setup_meta)

options(
    setup=Bunch(
        name='pydap.handlers.cdms',
        version='.'.join(str(d) for d in __version__),
        description='GrADS/grib handler for Pydap',
        long_description='''
Pydap is an implementation of the Opendap/DODS protocol, written from
scratch. This handler enables Pydap to serve GrADS gribbed files on the
network for Opendap clients.
        ''',
        keywords='GrADS grib ctl cdms opendap dods dap data science climate oceanography meteorology',
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
        author='Roberto De Almeida',
        author_email='rob@pydap.org',
        url='http://pydap.org/handlers.html#cdms',
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
            'cdat-lite>=6.0.alpha',
            'arrayterator>=1.0.1',
        ],
        entry_points="""
            [pydap.handler]
            cdms = pydap.handlers.cdms:Handler
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

