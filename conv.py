import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_localize import localized_module
from torch_dimcheck import dimchecked

import matplotlib.pyplot as plt

any_float=(torch.float16, torch.float32, torch.float64)
    
@dimchecked
def h_conv(x: ['b',     'f_in', 'xh', 'xw', 2],
           w: ['f_out', 'f_in', 'kh', 'kw', 2],
           pad=False) -> ['b', 'f_out', 'oh', 'ow', 2]:

    if pad:
        padding = w.shape[3] // 2
    else:
        padding = 0

    real = F.conv2d(x[..., 0], w[..., 0], padding=padding) - \
           F.conv2d(x[..., 1], w[..., 1], padding=padding)

    imag = F.conv2d(x[..., 0], w[..., 1], padding=padding) + \
           F.conv2d(x[..., 1], w[..., 0], padding=padding)

    return torch.stack([real, imag], dim=-1)

@localized_module
class HConv(nn.Module):
    def __init__(self, in_channels, out_channels, radius, order, pad=False):
        super(HConv, self).__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.radius = radius
        self.order = order
        self.pad = pad

        total_channels = in_channels * out_channels

        radial = torch.randn(total_channels, radius + 1, requires_grad=True)
        betas = torch.zeros(total_channels, requires_grad=True)
        nn.init.uniform_(betas, 0, 2 * 3.14)

        self.weights = Weights(radial, betas, order)

    @dimchecked
    def forward(self, t: ['b', 'fi', 'hi', 'wi', 2]) -> ['b', 'fo', 'ho', 'wo', 2]:
        kernel = self.weights.synthesize()
        kernel = kernel.reshape(
            self.out_channels, self.in_channels, self.weights.diam, self.weights.diam, 2
        )

        return h_conv(t, kernel, pad=self.pad)


class Weights(nn.Module):
    @dimchecked
    def __init__(self, r: ['n_f', 'r'], beta: ['n_f'], order):
        super(Weights, self).__init__()

        self.n_features = r.shape[0]
        self.radius = r.shape[1] - 1

        self.r = r
        self.diam = 2 * self.radius + 1

        self.beta = beta.reshape(-1, 1, 1)
        self.order = order

        self.precompute_bilinear()
        self.precompute_angles()
    
    def precompute_bilinear(self):
        # compute radii on grid
        xs = torch.linspace(-self.radius, self.radius, self.diam)
        xs = xs.reshape(1, -1)
        ys = xs.reshape(-1, 1)
        rs = torch.sqrt(xs ** 2 + ys ** 2)

        # compute floor, ceil and alpha for bilinear interpolation
        floor = torch.floor(rs)
        self.register_buffer('alpha', (rs - floor).reshape(1, self.diam, self.diam))
        self.register_buffer('floor', floor.to(torch.int64))
        self.register_buffer('ceil', torch.ceil(rs).to(torch.int64))

        # in `radial` we extend the radial function with a 0 at the end such that we
        # can redirect out of bounds accesses there. Here we do it
        self.ceil[self.ceil > self.radius] = self.radius + 1
        self.floor[self.ceil > self.radius] = self.radius + 1


    def precompute_angles(self):
        # compute angles on grid
        xs = torch.linspace(-1, 1, self.diam)
        xs = xs.reshape(1, -1)
        ys = xs.reshape(-1, 1)
        self.register_buffer('angles', torch.atan2(xs, ys).unsqueeze(0))

    @dimchecked
    def harmonics(self) -> ['f', 'd', 'd', 2]:
        real = torch.cos(self.order * self.angles + self.beta)
        imag = torch.sin(self.order * self.angles + self.beta)

        return torch.stack([real, imag], dim=-1)

    @dimchecked
    def radial(self) -> ['f', 'd', 'd']:
        # pad radial function with 0 so that we can redirect out of bounds
        # accesses there
        r_ = torch.cat([self.r, torch.zeros(self.n_features, 1)], dim=1)

        rf = r_[:, self.floor]
        rc = r_[:, self.ceil]
        return self.alpha * rc + (1 - self.alpha) * rf


    def lowpass(self, w):
        return w #TODO: actual filtering

    @dimchecked
    def synthesize(self) -> ['f', 'r', 'r', 2]:
        radial = self.radial().unsqueeze(-1)
        harmonics = self.harmonics()

        return self.lowpass(radial * harmonics)
