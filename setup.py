import os.path
import sys
from setuptools import setup

if sys.platform == 'win32':
    try:
        from cx_Freeze import setup, Executable
    except ImportError:
        raise ImportError('Failed to import cx_Freeze')

    zip_includes = [('gns3converter/configspec',
                     os.path.join('gns3converter', 'configspec'))]

    setup(
        name='gns3-converter',
        version=__import__('gns3converter').__version__,
        packages=['gns3converter'],
        url='https://github.com/dlintott/gns3-converter',
        license='GPLv3+',
        author='Daniel Lintott',
        author_email='daniel@serverb.co.uk',
        description='Convert old ini-style GNS3 topologies (<=0.8.7) to the '
                    'newer version 1+ JSON format',
        install_requires=['configobj'],
        package_data={'gns3converter': ['configspec']},
        options={'build_exe': {'namespace_packages': 'gns3converter',
                               'packages': 'gns3converter',
                               'zip_includes': zip_includes,
                               'include_msvcr': True
                               }
                 },
        executables=[Executable("gns3-converter.py")]
    )
else:
    setup(
        name='gns3-converter',
        version=__import__('gns3converter').__version__,
        packages=['gns3converter'],
        url='https://github.com/dlintott/gns3-converter',
        license='GPLv3+',
        author='Daniel Lintott',
        author_email='daniel@serverb.co.uk',
        description='Convert old ini-style GNS3 topologies (<=0.8.7) to the '
                    'newer version 1+ JSON format',
        long_description=open("README.rst", "r").read(),
        test_suite='tests',
        install_requires=['configobj'],
        package_data={'gns3converter': ['configspec']},
        entry_points={'console_scripts':
                    ['gns3-converter = gns3converter.main:main']},
        platforms='any',
        classifiers=['Development Status :: 5 - Production/Stable',
                     'Environment :: Console',
                     'Intended Audience :: Education',
                     'Intended Audience :: Information Technology',
                     'License :: OSI Approved :: GNU General Public License '
                     'v3 or later (GPLv3+)',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.3',
                     'Programming Language :: Python :: 3.4',
                     'Topic :: Education',
                     'Topic :: Utilities']
    )