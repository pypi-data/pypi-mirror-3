import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "satchmo_payment_payworld",
    version = "0.1.1",
    author = "Ivan A. Anishchuk",
    author_email = "anishchuk_ia@lavabit.com",
    description = ("Intergration pay-world.ru for satchmo"),
    license = "CC0",
    keywords = "payment django satchmo integration",
    url = "https://bitbucket.org/ib_soft/satchmo_payment_payworld",
    packages=['satchmo_payment_payworld'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 2 :: Only",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    ],
    install_requires=[
        'setuptools',
        'django',
        'django_payworld',
        'Satchmo'
    ],
)
