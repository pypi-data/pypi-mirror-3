from setuptools import setup
 
version = '0.1'
 
LONG_DESCRIPTION = """
======
Scrapr
======

Scrapr makes it easy to setup a model for finding specific tags, links, or text on a web page. 
"""
 
setup(
    name='scrapr',
    version=version,
    description="""Scrapr makes it easy to setup a model for finding specific tags, links, or text on a web page.""",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
    ],
    keywords='web,scraping',
    author='Brian Jinwright',
    author_email='team@ipoots.com',
    maintainer='Brian Jinwright',
    packages=['scrapr'],
    url='https://bitbucket.org/brianjinwright/scrapr',
    license='MIT',
    install_requires=['beautifulsoup>=3.2.1','beautifulsoup4>=4.0.5'],
    include_package_data=True,
    zip_safe=False,
)