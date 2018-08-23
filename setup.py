from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(  name='Karelia',
        version='2.0.7',
        description='Python library for euphoria.io',
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Pouncy Silverkitten',
        author_email='pouncy.sk@gmail.com',
        url='https://github.com/pouncysilverkitten/karelia',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",],
        install_requires=[
            'websocket-client'
        ],
        py_modules=['karelia'],)
