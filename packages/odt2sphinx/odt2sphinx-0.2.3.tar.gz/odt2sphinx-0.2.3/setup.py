from setuptools import setup, find_packages

setup(
    name="odt2sphinx",
    version="0.2.3",
    description="An OpenDocument to sphinx converter.",
    long_description=open("README.rst").read(),
    author="Christophe de Vienne",
    author_email="<cdevienne@gmail.com>",
    url='https://bitbucket.org/cdevienne/odt2sphinx',
    install_requires=[
        'six', 'PIL'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
    packages=find_packages(exclude=['ez_setup']),
    entry_points={
        'console_scripts': [
            'odt2sphinx = odt2sphinx.odt2sphinx:main'
        ]
    }
)
