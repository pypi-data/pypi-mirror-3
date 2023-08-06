"""This module implements a two-stage HMAX-like model.

This module implements a multi-scale analysis by applying single-scale Gabors to
a scale pyramid of the input image. This is similar to the configuration used by
Mutch & Lowe (2008).

"""

# Copyright (c) 2011 Mick Thomure
# All rights reserved.
#
# Please see the file COPYING in this distribution for usage terms.

from scipy.ndimage.interpolation import zoom

from glimpse.models.misc import BaseState, Whiten
from glimpse.models.viz2.model import Model as Viz2Model
from glimpse.models.viz2.model import Layer
from glimpse.util import kernel
from .params import Params

class State(BaseState):
  """A container for the :class:`Model` state."""
  pass

class Model(Viz2Model):
  """Create a 2-part, HMAX-like hierarchy of S+C layers."""

  #: The datatype associated with layer descriptors for this model.
  LayerClass = Layer

  #: The parameters type associated with this model.
  ParamClass = Params

  #: The datatype associated with network states for this model.
  StateClass = State

  @property
  def s1_kernel_shape(self):
    """The expected shape of the S1 kernels array, including band structure.

    :rtype: tuple of int

    """
    p = self.params
    return p.s1_num_orientations, p.s1_num_phases, p.s1_kwidth, p.s1_kwidth

  @property
  def s1_kernels(self):
    """The set of S1 kernels, which is generated if not set.

    :returns: S1 kernels indexed by orientation, and phase.
    :rtype: 4D ndarray of float

    """
    # if kernels array is empty, then generate it using current model parameters
    if self._s1_kernels == None:
      p = self.params
      self._s1_kernels = kernel.MakeGaborKernels(
          kwidth = p.s1_kwidth,
          num_orientations = p.s1_num_orientations,
          num_phases = p.s1_num_phases, shift_orientations = True,
          scale_norm = self.s1_kernels_are_normed)
    return self._s1_kernels

  def BuildS1FromRetina(self, retina):
    """Apply S1 processing to some existing retinal layer data.

    .. note::

       This method pools over phase, so the output has only scale and
       orientation bands.

    :param retina: Result of retinal layer processing.
    :type retina: 2D ndarray of float
    :return: S1 maps indexed by scale and orientation.
    :rtype: list of 3D ndarray of float

    """
    # Create scale pyramid of retinal map
    p = self.params
    retina_scales = [ zoom(retina, 1 / p.scale_factor ** scale)
        for scale in range(p.num_scales) ]
    # Reshape kernel array to be 3-D: index, 1, y, x
    s1_kernels = self.s1_kernels.reshape((-1, 1, p.s1_kwidth, p.s1_kwidth))
    s1s = []
    backend_op = getattr(self.backend, p.s1_operation)
    for scale in range(p.num_scales):
      # Reshape retina to be 3D array
      retina = retina_scales[scale]
      retina_ = retina.reshape((1,) + retina.shape)
      s1_ = backend_op(retina_, s1_kernels, bias = p.s1_bias, beta = p.s1_beta,
          scaling = p.s1_sampling)
      # Reshape S1 to be 4D array
      s1 = s1_.reshape((p.s1_num_orientations, p.s1_num_phases) + \
          s1_.shape[-2:])
      # Pool over phase.
      s1 = s1.max(1)
      # Append 3D array to list
      s1s.append(s1)
    return s1s

  def BuildC1FromS1(self, s1s):
    """Compute the C1 layer activity from multi-scale S1 activity.

    :param s1s: S1 maps indexed by scale.
    :type s1s: list of 3D ndarray of float, or 4D ndarray of float
    :returns: C1 maps indexed by scale and orientation.
    :rtype: list of 3D ndarray of float

    """
    p = self.params
    c1s = [ self.backend.LocalMax(s1, kwidth = p.c1_kwidth,
        scaling = p.c1_sampling) for s1 in s1s ]
    if p.c1_whiten:
      # Whiten each scale independently, modifying values in-place.
      map(Whiten, c1s)
    return c1s

  def BuildS2FromC1(self, c1s):
    """Compute the S2 layer activity from multi-scale C1 activity.

    :param c1s: C1 maps indexed by scale and orientation.
    :type c1s: 4D ndarray of float, or list of 3D ndarray of float
    :returns: S2 maps indexed by scale and prototype.
    :rtype: list of 3D ndarray of float

    """
    if self.s2_kernels == None or len(self.s2_kernels[0]) == 0:
      raise Exception("Need S2 kernels to compute S2 layer activity, but none "
          "were specified.")
    kernels = self.s2_kernels[0]
    if len(c1s) == 0:
      return []
    p = self.params
    s2s = []
    backend_op = getattr(self.backend, p.s2_operation)
    for scale in range(p.num_scales):
      c1 = c1s[scale]
      s2 = backend_op(c1, kernels, bias = p.s2_bias, beta = p.s2_beta,
          scaling = p.s2_sampling)
      # Append 3D array to list.
      s2s.append(s2)
    return s2s

# Add (circular) Model reference to State class.
State.ModelClass = Model
