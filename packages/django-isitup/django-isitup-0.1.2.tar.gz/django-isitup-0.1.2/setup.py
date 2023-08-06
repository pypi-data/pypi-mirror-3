from setuptools import setup, find_packages

setup(
    name='django-isitup',
    version=__import__('isitup').__version__,
    license="BSD",

    install_requires = [
        'django-extensions',],

    description='A simple reusable application for managing a small orgs governance in a Django application.',
    long_description=open('README.md').read(),

    author='Colin Powell',
    author_email='colin@onecardinal.com',

    url='http://github.com/powellc/django-isitup',
    download_url='http://github.com/powellc/django-isitup/downloads',

    include_package_data=True,

    packages=['isitup'],

    zip_safe=True,
    classifiers=[ 'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
