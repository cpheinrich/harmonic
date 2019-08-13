from setuptools import setup


def required_packages():
    PACKAGES = [
        'torch==1.1.0',
        'torchvision==0.2.2.post3'
    ]
    return PACKAGES


setup(
    name='harmonic-networks',
    version='0.0.3',
    description='PyTorch reimplementation of harmonic networks',
    packages=['harmonic', 'torch_dimcheck', 'torch_localize'],
    install_requires=required_packages(),
    author='Michał Tyszkiewicz',
    author_email='michal.tyszkiewicz@gmail.com',
)
