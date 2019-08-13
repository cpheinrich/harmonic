# harmonic
Reimplementation of harmonic networks in PyTorch. Original TensorFlow implementation is
[here](https://github.com/deworrall92/harmonicConvolutions). The reimplementation is not one to one. We reimplement
harmonic convolutions, generalizing them to have per-radius phase offsets. Nonlinearities use a multiplicative
"attentional" model, rather than the C-ReLU proposed by Worrall et al. Additionally, we split the library into two modules:
`d2` which contains the standard harmonic network implementation for 2d domains and `d3`, which is a 3d version, arranged to
ensure equivaraince to rotations along (x, y) axes and allowing arbitrary kernels along z axis. This is useful for volume data
which is anisotropic along one dimension, for instance slice microscopy.

# Installation
1. Clone this repository
2. Execute `python setup.py install`. In some case this doesn't work properly and `python setup.py develop`
   is necessary instead. I am not sure what is the reason for these issues
OR
1. Simply add `git+https://github.com/cpheinrich/harmonic@master` to your requirements.txt file

# Examples
In examples/mnist2d one can find reimplementation of the RotMNIST experiment from Worrall et al., which requires manually
downloading the data using [their code](https://github.com/deworrall92/harmonicConvolutions/blob/master/MNIST-rot/run_mnist.py).
