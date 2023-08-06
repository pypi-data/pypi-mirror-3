from setuptools import setup, find_packages

required = ['requests-oauth >= 0.3.0']

setup(
    author='Factual Driver Team',
    name='factual-api',
    version='0.9.0',
    description='Official Python driver for the Factual public API',
    long_description=open('README.md').read(),
    url='http://github.com/Factual/factual-python-driver',
    license='Apache License',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    keywords=['factual'],
    packages=find_packages(),
    install_requires=required
)
