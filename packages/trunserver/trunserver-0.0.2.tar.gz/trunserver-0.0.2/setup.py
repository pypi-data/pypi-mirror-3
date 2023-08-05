from setuptools import setup, find_packages

setup(
    name='trunserver',
    version='0.0.2',
    description='Twisted based Django runserver replacement.',
    long_description = open('README.rst', 'r').read(),
    author='Gregory Armer',
    author_email='greg@codelounge.org',
    license='MIT',
    url='https://github.com/gregarmer/trunserver',
    packages = find_packages(),
    dependency_links = [],
    install_requires = [
        'twisted',
    ],
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
)
