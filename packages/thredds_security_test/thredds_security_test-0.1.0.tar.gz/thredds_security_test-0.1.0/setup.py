try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='thredds_security_test',
    version="0.1.0", 
    description='THREDDS Data Server security configuration test utilities',
    author='Richard Wilkinson',
    long_description=open('README').read(),
    license='BSD - See LICENCE file for details',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'thredds_test_catalog_access = bin.check_catalog:main',
            'thredds_test_file_access = bin.check_files:main',
            'thredds_test_url_access = bin.check_url:main'
            ]
        }
)
