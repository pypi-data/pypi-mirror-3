from setuptools import setup, find_packages

setup(
    name='django-dishes',
    version=__import__('dishes').__version__,
    license="BSD",

    install_requires = [],

    description='We need menus of delicious food that people can order and have delivered.',
    long_description=open('README').read(),

    author='Colin Powell',
    author_email='colin@onecardinal.com',

    url='http://github.com/powellc/django-dishes',
    download_url='http://github.com/powellc/django-dishes/downloads',

    include_package_data=True,

    packages=['dishes'],

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
