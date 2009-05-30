from setuptools import setup, find_packages

version = '0.1b1'

setup(name='git-svn-helpers',
    version=version,
    description="Command-line tools to make git-svn simple",
    long_description=open("README.txt").read(),
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control',
        "License :: OSI Approved :: BSD License",
    ],
    keywords='git svn',
    author='Tom Lazar',
    author_email='tom@tomster.org',
    url='http://github.com/tomster/git-svn-helpers',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        "jarn.mkrelease",
    ],
    entry_points="""
        # -*- Entry points: -*-
        [console_scripts]
        gitify=gitsvnhelpers.gitify:main
        gs-clone=gitsvnhelpers.clone:main
    """,
    )
