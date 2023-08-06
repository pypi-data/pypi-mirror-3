import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

version = '0.2'
require = ['pyramid', 'soapbox']

setup(name='pyramid_soap',
    version=version,
    description="Soap for pyramid.",
    long_description="""\
    """,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    keywords='web pyramid pylons soap soapbox',
    author='Gines Martinez Sanchez',
    author_email='ginsmar@artgins.com',
    url='https://bitbucket.org/artgins/pyramid_soap',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=require,
    tests_require=require,
    test_suite="pyramid_soap",
    entry_points="""
    # -*- Entry points: -*-
    """,
    paster_plugins=['pyramid'],
)
