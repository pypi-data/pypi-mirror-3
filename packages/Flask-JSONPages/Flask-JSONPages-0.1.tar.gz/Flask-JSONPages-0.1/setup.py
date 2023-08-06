from setuptools import setup, find_packages

setup(
    name='Flask-JSONPages',
    version='0.1',
    url='https://github.com/munhitsu/Flask-JSONPages',
    license='BSD',
    author='Mateusz Lapsa-Malawski',
    author_email='mateusz@munhitsu.com',
    description='Provides static pages to a Flask application based on JSON',
    long_description=__doc__,
    packages=find_packages(),
    namespace_packages=['flask_jsonpages'],
    # test pages
    package_data={'': ['pages*/*.*', 'pages/*/*.*', 'pages/*/*/*.*']},
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

