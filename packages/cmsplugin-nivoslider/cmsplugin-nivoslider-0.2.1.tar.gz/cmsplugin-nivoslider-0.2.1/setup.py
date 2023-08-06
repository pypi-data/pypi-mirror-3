# -*- coding:utf-8 -*-
#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages

setup(
    name='cmsplugin-nivoslider',
    version='0.2.1',
    author='APSL · Bernardo Cabezas Serra',
    author_email='bcabezas@apsl.net',
    packages = find_packages(),
    license='MIT',
    description = "Simple Nivo Slider plugin for django-cms",
    long_description=open('README.rst').read(),
    install_requires = ['django', 'easy-thumbnails',],
)
