from setuptools import setup

setup(
    name='django-cacheops',
    version='0.8',
    author='Alexander Schepanovski',
    author_email='suor.web@gmail.com',

    description='slick ORM cache and invalidation for Django',
    long_description=open('README.rst').read(),
    url='http://github.com/Suor/django-cacheops',
    license='BSD',

    packages=['cacheops'],
    install_requires=[
        'django>=1.2',
        'redis>=2.2.4',
        'simplejson>=2.1.5',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',

        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
