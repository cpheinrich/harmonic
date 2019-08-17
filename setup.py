from setuptools import setup, find_packages


def required_packages():
    PACKAGES = [
        'torch==1.1.0',
        'torchvision==0.2.2.post3'
    ]
    return PACKAGES


setup(
    name='harmonic-networks',
    version='0.0.3',
    description='PyTorch reimplementation of harmonic networks. Forked and modified from https://github.com/jatentaki/harmonic',
    packages=find_packages(),
    install_requires=required_packages(),
    author='Chris Heinrich',
    author_email='cpheinrich@gmail.com',
)
