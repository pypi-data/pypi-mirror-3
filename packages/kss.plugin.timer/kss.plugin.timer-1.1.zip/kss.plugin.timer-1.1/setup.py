from setuptools import setup, find_packages

readme = open('README.txt').read().strip()
history = open('CHANGES.rst').read().strip()

long_description = readme + '\n\n' + history
version = '1.1'

setup(
    name='kss.plugin.timer',
    version=version,
    description="Timer plugin for KSS",
    long_description=long_description,
    author="Guido Wesdorp and Zest software",
    author_email="info@zestsoftware.nl",
    url="https://plone.org/products/extreme-management-tool/",
    install_requires=["kss.base", "setuptools"],
    packages=find_packages(),
    namespace_packages=['kss', 'kss.plugin'],
    include_package_data=True,
    test_suite='kss.plugin.timer.tests.test_suite',
    entry_points={
        'kss.plugin': [
            'kss.plugin.timer=kss.plugin.timer.config:Kss.plugin.timer'
            ],
        },
)
