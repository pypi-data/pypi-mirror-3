from setuptools import setup, find_packages

setup(
    name='django-classroom',
    version=__import__('classroom').__version__,
    license="BSD",

    install_requires = [],

    description='An application for managing classroom details on a school website.',
    long_description=open('README').read(),

    author='Colin Powell',
    author_email='colin@onecardinal.com',

    url='http://github.com/powellc/django-classroom',
    download_url='http://github.com/powellc/django-classroom/downloads',

    include_package_data=True,

    packages=['classroom'],

    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
