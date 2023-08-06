from setuptools import setup, find_packages

version = '0.2'

setup(
    name='django-templatepages',
    version = version,
    description = "Django app for mapping URLs to templates on the filesystem.",
    long_description = open('README.md').read(),
    classifiers = [],
    keywords = '',
    author = 'Bryan Chow',
    author_email = '',
    url = 'https://github.com/bryanchow/django-templatepages',
    download_url = 'https://github.com/bryanchow/django-templatepages/tarball/master',
    license = 'BSD',
    packages = find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'django',
    ],
)
