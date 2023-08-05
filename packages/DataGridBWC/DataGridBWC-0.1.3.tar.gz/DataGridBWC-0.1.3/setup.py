"""
DataGridBWC
======================

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Source Code
---------------

The code is available from the `bitbucket repo <http://bitbucket.org/rsyring/datagridbwc/>`_.

The `DataGridBWC tip <http://bitbucket.org/rsyring/datagridbwc/get/tip.zip#egg=datagridbwc-dev>`_
is installable via `easy_install` with ``easy_install DataGridBWC==dev``
"""

from setuptools import setup, find_packages

from datagridbwc import VERSION

setup(
    name='DataGridBWC',
    version=VERSION,
    description="A BlazeWeb component for turning SQLAlchemy recordsets into HTML tables",
    long_description = __doc__,
    classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    ],
    author='Randy Syring',
    author_email='rsyring@gmail.com',
    url='http://bitbucket.org/rsyring/datagridbwc/',
    license='BSD',
    packages=find_packages(exclude=['datagridbwc_*']),
    tests_require=['webtest'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'BlazeWeb>=0.3.0',
        'SQLAlchemyBWC>=0.1',
        "python-dateutil<=1.9.999"
    ],
)
