try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='fixture-yaml',
    version='0.1.2',
    author='Ilya Shabalin',
    author_email='ilja.shabalin@gmail.com',
    url='https://bitbucket.org/w31rd0/fixture-yaml',
    description=(
        'fixture-yaml is an extension that adds YAML support '
        'to fixture library'),
    classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
    ],
    license='Public Domain',
    py_modules=['fixture_yaml'],
    packages=find_packages(exclude=['ez_setup', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'pyyaml',
        'fixture',
    ],
    setup_requires=[
        'nose',
    ],
    test_suite='nose.collector',
)
