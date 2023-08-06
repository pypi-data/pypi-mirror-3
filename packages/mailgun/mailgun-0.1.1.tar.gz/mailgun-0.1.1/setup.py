import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(

    name='mailgun',

    version='0.1.1',

    author='Mailgun Inc.',

    author_email='admin@mailgunhq.com',

    description='Python wrapper for Mailgun REST API',

    long_description=read('README'),

    url='http://mailgun.net',

    packages=find_packages(),

    install_requires=['pyactiveresource==1.0.1'],

    classifiers=[

        'Intended Audience :: Developers',

        'Programming Language :: Python',

        'License :: OSI Approved :: BSD License',

    ],

    license='BSD',
)
