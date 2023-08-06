# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


version = '0.6'
maintainer = 'Rok Garbas'
author = 'Ivan Price'


setup(
    name='acted.projects',
    version=version,
    description="",
    long_description="",
    classifiers=[
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Zope",
        "Framework :: Zope2",
        "Framework :: Plone",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Natural Language :: French",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Internet :: WWW/HTTP",
        ],
    keywords='plone',
    author='%s,  Agence d’Aide à la Coopération Technique Et au Développement' % author,
    author_email='ivan.price@acted.org',
    maintainer=maintainer,
    url='',
    license='Proprietary',
    packages=find_packages(),
    namespace_packages=['acted'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
#    extras_require = {
#        'test': [
#            'plone.app.testing',
#            ]
#        },
    )
