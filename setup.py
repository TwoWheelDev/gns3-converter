from setuptools import setup

setup(
    name='gns3-converter',
    version='0.1',
    packages=['gns3converter'],
    url='https://github.com/dlintott/gns3-converter',
    license='GNU General Public License v3 (GPLv3)',
    author='Daniel Lintott',
    author_email='daniel@serverb.co.uk',
    description='<TODO>',
    test_suite='tests',
    install_requires=['configobj'],
    package_data={'gns3converter': ['configspec']},
    entry_points={'console_scripts': ['converter = gns3converter.main:main']}
)
