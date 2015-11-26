from setuptools import setup, find_packages

setup(
    name='mygrid',
    packages=find_packages(),
    version='0.1',
    description='A package to represent a electric grid \
    topology with extensions to make power flow and short circuit \
    analysis',
    install_requires=['numpy>=1.8.2', 'terminaltables'],
    author='Lucas S Melo',
    author_email='lucassmelo@dee.ufc.br',
)
