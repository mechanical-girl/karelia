from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(  name='kareliapy',
        version='2.2.1',
        description='Python library for euphoria.io',
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='StruanDW',
        author_email='struan@duncan-wilson.co.uk',
        url='https://github.com/struandw/karelia',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",],
        install_requires=[
            'websocket-client',
        ],
        py_modules=['karelia'],)
