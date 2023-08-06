from setuptools import setup, find_packages
import ella

setup(
    name='ella',
    version=ella.__versionstr__,
    description='Ella - Django powered CMS',
    long_description='\n'.join((
        'Ella Django CMS Project',
        '',
        'content management system written in Django',
        '',
    )),
    author='Ella Development Team',
    author_email='dev@ella-cms.com',
    license='BSD',
    url='https://github.com/ella/ella',

    packages=find_packages(
        where='.',
        exclude=('doc', 'test_ella', )
    ),

    include_package_data=True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        'setuptools>=0.6b1',
        'Django>=1.3.1',
        'south>=0.7',
        'jsonfield'
    ],
    test_suite='test_ella.run_tests.run_all'

)
