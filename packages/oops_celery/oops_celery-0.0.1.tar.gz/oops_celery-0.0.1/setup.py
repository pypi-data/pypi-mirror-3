import os

from setuptools import setup, find_packages

setup(
    name='oops_celery',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    maintainer='Launchpad developers',
    maintainer_email='launchpad-devs@lists.launchpad.net',
    description='Oops integration for celery',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    license='LGPLv3',
    url='http://launchpad.net/python-oops-celery',
    download_url='https://launchpad.net/python-oops-celery/+download',
    test_suite='oops_celery.tests',
    install_requires = [
        'oops',
        'celery',
        ],
    # Auto-conversion to Python 3.
    use_2to3=True,
    )
