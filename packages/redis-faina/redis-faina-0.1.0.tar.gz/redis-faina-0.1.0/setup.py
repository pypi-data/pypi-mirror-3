from distutils.core import setup

setup(
    name = "redis-faina",
    version = "0.1.0",
    author = "Mike Krieger",
    author_email = "mikeyk@instagram.com",
    maintainer = "Rick Branson",
    maintainer_email = "rick@diodeware.com",
    url = "http://github.com/Instagram/redis-faina",
    packages = [ "redis_faina" ],
    scripts = [ "bin/redis-faina" ],
    license = "LICENSE",
    description = "Query analyzer that parses Redis MONITOR command output"
)
