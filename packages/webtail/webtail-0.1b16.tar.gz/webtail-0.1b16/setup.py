# coding: utf-8
from setuptools import setup, find_packages

setup(name='webtail',
    description='Tornado-based log viewer',
    version='0.1b16',
    license='BSD License',
    author='Mikhail Lukyanchenko',
    author_email='ml@uptimebox.ru',
    url='https://bitbucket.org/uptimebox/webtail',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    packages=find_packages(),
    include_package_data = True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'tornado>=2.2',
        'anyjson',
    ],
    entry_points = {
        'console_scripts': [
            'webtail = webtail:main',
        ]
    }
)
