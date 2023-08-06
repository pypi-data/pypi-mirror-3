from setuptools import setup

setup(
    name='Flask-FAS',
    version='0.1.0',
    url='http://fedorahosted.org/flask-fas',
    license='BSD',
    author='Ian Weller',
    author_email='ianweller@fedoraproject.org',
    description='Adds Fedora Account System support to Flask',
    py_modules=['flask_fas'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'python-fedora >= 0.3.17',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
