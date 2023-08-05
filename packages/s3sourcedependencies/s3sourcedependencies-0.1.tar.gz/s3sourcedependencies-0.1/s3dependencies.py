import re
import tempfile
from distutils import spawn
from distutils.errors import DistutilsSetupError


valid_s3_url = re.compile(
    "s3://([a-z0-9][a-z0-9\-\.]+)/([\w][\w\W]*)")


def load(dist, attr, value):
    if not (isinstance(value, list) or isinstance(value, tuple)):
        raise DistutilsSetupError((
            "You need to specify either a list or a tuple of valid S3 URLs "
            "for '%s'") % attr)

    for dependency in value:
        package_key = _validate(dependency)
        _install_from_s3(package_key)


def _validate(dependency):
    """Validate a specified dependency URL."""
    print "Checking package %s" % dependency

    match = valid_s3_url.match(dependency)
    if not match:
        raise DistutilsSetupError(
            "An invalid s3 dependency URL was specified: "
            "s3://<bucket_name>/<key> expected")

    bucket_name, key_name = match.groups()

    import boto
    s3 = boto.connect_s3()
    bucket = s3.get_bucket(bucket_name, validate=False)
    if not bucket:
        raise DistutilsSetupError(
            "Invalid bucket name specified: %s" % bucket_name)

    key = bucket.get_key(key_name)
    if not key:
        raise DistutilsSetupError(
            "Could not fetch the specified package: %s (Not Found)" % key_name)

    return key


def _install_from_s3(key):
    """Install the package from the specified s3 key."""
    print "Downloading package %s from s3://%s" % (key.name, key.bucket.name)

    with tempfile.NamedTemporaryFile(suffix='.tar.gz') as package_file:
        key.get_contents_to_file(package_file)
        package_file.flush()
        spawn.spawn(["pip", "install", package_file.name])
