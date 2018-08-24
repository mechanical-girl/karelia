from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(  name='Karelia',
        version='2.0.8',
        description='Python library for euphoria.io',
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='StruanDW',
        author_email='struan@duncan-wilson.co.uk',
        url='https://github.com/pouncysilverkitten/karelia',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",],
        install_requires=[
            'websocket-client'
        ],
        py_modules=['karelia'],)
