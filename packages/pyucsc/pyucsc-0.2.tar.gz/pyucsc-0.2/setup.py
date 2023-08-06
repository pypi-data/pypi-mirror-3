from setuptools import setup

setup(
    name='pyucsc',
    version='0.2',
    description='Bindings to UCSC genome browser tables',
    author='James Casbon',
    author_email='james.casbon@popgentech.com',
    packages=['ucsc'],
    install_requires=[
        'numpy',
        'SQLAlchemy',
        'pyyaml',
        'fastinterval',
    ],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
      ],
    keywords='bioinformatics ucsc genome',
    license='License :: OSI Approved :: BSD License'
)
