from setuptools import setup, find_packages

setup(
    name='django-featured',
    version=__import__('featured').__version__,
    license="BSD",

    install_requires = [],

    description='An application for starting new django applications.',
    long_description=open('README').read(),

    author='Colin Powell',
    author_email='colin@onecardinal.com',

    url='http://github.com/powellc/django-featured',
    download_url='http://github.com/powellc/django-featured/downloads',

    include_package_data=True,

    packages=['featured'],

    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
