import os
from setuptools import setup, find_packages


setup(
    name='django-user-extension',
    version='1.0.0',
    description="Subclass the Django User model to your heart's delight.",
    long_description=file(
        os.path.join(os.path.dirname(__file__), 'README.rst')
    ).read(),
    author='David Bennett',
    author_email='david@dbinit.com',
    url='http://bitbucket.org/dbinit/django-user-extension/',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    zip_safe=False,
    install_requires='django-model-utils>=1.0.0',
)
