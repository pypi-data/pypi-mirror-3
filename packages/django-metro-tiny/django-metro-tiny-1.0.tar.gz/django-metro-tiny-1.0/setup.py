from setuptools import setup, find_packages

setup(
    name='django-metro-tiny',
    version='1.0',
    description='Metro stations and lines models for Django',
    author='Konstantin Korikov',
    author_email='lostclus@gmail.com',
    url='http://code.google.com/p/django-metro-tiny/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    long_description="""
    Simple Django application to provide metro stations and lines models. Based
    on django-cities-tiny.
    """,
    license = 'MIT',
    install_requires=[
        'django-cities-tiny',
        ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
