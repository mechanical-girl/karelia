from distutils.core import setup

setup(  name='Karelia',
        version='2.0.6',
        description='Python library for euphoria.io',
        author='Pouncy Silverkitten',
        author_email='pouncy.sk@gmail.com',
        url='https://github.com/pouncysilverkitten/karelia',
        install_requires=[
            'websocket-client',
            'munch'
        ],
        py_modules=['karelia'],)
