====================
s3sourcedependencies
====================

Usage
-----

Extends setuptools by adding a new setup keyword ``s3dependencies`` which will
download and install the specified dependencies from S3.

An example::

    setup(
        name='demo',
        version='0.5.1',
        author='Ion Scerbatiuc',
        packages=find_packages(),
        setup_requires=['s3sourcedependencies'],
        s3dependencies=[
            's3://my.sdist.bucket/private.dependency-0.x.tar.gz',
            's3://my.other.sdist.bucket/other.private.dependency-1.x.tar.gz',
        ],
    )

In order for this to work you will need to have the ``AWS_ACCESS_KEY_ID`` and
``AWS_SECRET_ACCESS_KEY`` environment variables available to the process
installing the package.

Can be combined with `s3sourceuploader <http://github.com/pbs/s3sourceuploader>`_
to package, distribute and use private packages as dependencies for other
private packages.

Current limitations
-------------------

- only .tar.gz source distributions are supported
- only buckets available to a single AWS account can be used
- the private packages are downloaded each time regardless if they are already installed
