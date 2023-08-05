from setuptools import setup, find_packages

setup(
    name="lazyrange",
    version="0.0.2",
    description="A very lazy range object",
    author="invlpg",
    author_email="invlpg@gmail.com",
    url="http://pypi.python.org/pypi/lazyrange",
    license="MIT",
    packages=find_packages(),
    test_suite='nose.collector',
)
