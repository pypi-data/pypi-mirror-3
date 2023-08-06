from setuptools import setup, find_packages
from sunlightcongress import __version__

setup(
    name='django-sunlightcongress',
    version=__version__,
    description='A Django interface to the Sunlight Foundation Congress API',
    keywords=(
        'america, united states, politics, congress, senate, house, '
        'sunlight, sunlight foundation'
    ),
    author='Chuck Harmston',
    author_email='chuck@chuckharmston.com',
    url='https://github.com/chuckharmston/django-sunlightcongress',
    license='MIT',
    package_dir={
        'sunlightcongress': 'sunlightcongress',
    },
    packages=find_packages(),
    install_requires=[
        'sunlight==1.1.5',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications',
    ],
)