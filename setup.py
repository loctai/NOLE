from setuptools import setup

setup(
    name='myapp',
    packages = ['myapp'],
    include_packages_data =True,
    install_requires =[
        'flask',
    ],
)