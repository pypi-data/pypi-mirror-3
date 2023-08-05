# coding: utf-8
from setuptools import setup, find_packages

setup(name='authgoogle-middleware',
    description='Google authentication middleware',
    version='0.2.1',
    license='BSD License',
    author='Mikhail Lukyanchenko',
    author_email='ml@uptimebox.ru',
    url='https://bitbucket.org/uptimebox/authgoogle-middleware',
    py_modules=['authgoogle_middleware'],
    install_requires=[
		'werkzeug>=0.6.2',
		'python-openid',
	],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    ]
)
