"""Miscellaneous functions related to images and image processing."""

# Copyright (c) 2011 Mick Thomure
# All rights reserved.
#
# Please see the file COPYING in this distribution for usage terms.

from garray import ACTIVATION_DTYPE, PadArray
import numpy as np
from scipy import fftpack
import sys

def ImageToArray(img, array = None, transpose = True):
  """Load image data into a 2D numpy array.

  :param img: Image to read.
  :type img: PIL.Image
  :param ndarray array: Output array. If unspecified, one will be generated
     automatically.
  :param bool transpose: Whether image data should be transposed before
     returning.
  :returns: Array containing image data. Note that this may be non-contiguous.
  :rtype: ndarray

  """
  def MakeBuffer():
    if img.mode == 'L':
      return np.empty(img.size, dtype = np.uint8)
    elif img.mode == 'RGB':
      return np.empty(img.size + (3,), dtype = np.uint8)
    elif img.mode == 'F':
      return np.empty(img.size, dtype = np.float)
    elif img.mode == '1':
      return np.empty(img.size, dtype = np.bool)
    raise Exception("Can't load data from image with mode: %s" % img.mode)
  def CopyImage(dest):
    img_data = img.load()
    for idx in np.ndindex(img.size):
      dest[idx] = img_data[idx]
    return dest
  def CheckArrayShape():
    shape = list(img.size)
    if transpose:
      shape = shape[::-1]
    shape = tuple(shape)
    assert shape == array.shape, "Array has wrong shape: expected %s but got" \
        "%s" % (shape, array.shape)
  if array != None:
    if not transpose:
      CheckArrayShape()
      return CopyImage(array)
    else:
      CheckArrayShape()
      # copy image to new buffer, copy buffer.T to array
      array[:] = CopyImage(MakeBuffer()).T
      return array
  else:
    if not transpose:
      return CopyImage(MakeBuffer())
    else:
      return CopyImage(MakeBuffer()).T
  assert False, "Internal logic error!"

def ShowImage(img, fname = None):
  """Display an image to the user."""
  if sys.platform == "darwin":
    img.show()
  else:
    ShowImageOnLinux(img, fname)

def ShowImageOnLinux(img, fname = None):
  """Display an image to the user under Linux."""
  dir = TempDir()
  if not fname or '..' in fname:
    fname = 'img.png'
  path = dir.MakePath(fname)
  img.save(path)
  RunCommand("eog -n %s" % path, False, False)

def PowerSpectrum2d(image):
  """Compute the 2-D power spectrum for an image.

  :param image: Image data.
  :type image: 2D ndarray
  :returns: Squared amplitude from FFT of image.
  :rtype: 2D ndarray

  """
  from scipy.fftpack import fftshift, fft2
  return np.abs(fftshift(fft2(image))) ** 2

def PowerSpectrum(image, width = None):
  """Get the 1-D power spectrum (squared-amplitude at each frequency) for a
  given input image. This is computed from the 2-D power spectrum via a
  rotational average.

  :param image: Image data.
  :type image: 2D ndarray
  :param int width: Width of image to use for FFT (i.e., image width plus
     padding). By default, this is the width of the image.
  :returns: Array whose rows contain the value, sum, and count of bins in the
     power histogram.

  """
  # from: http://www.astrobetter.com/fourier-transforms-of-images-in-python/
  assert image.ndim == 2
  if width != None:
    image = PadArray(image,
        np.repeat(width, 2),  # shape of padded array
        0)  # border value
  f2d = PowerSpectrum2d(image)
  # Get sorted radii.
  x, y = np.indices(f2d.shape)
  center_x = (x.max() - x.min()) / 2.0
  center_y = (y.max() - y.min()) / 2.0
  r = np.hypot(x - center_x, y - center_y)
  ind = np.argsort(r.flat)
  r_sorted = r.flat[ind]
  # Bin the radii based on integer values. First, find the location (offset) for
  # the edge of each bin.
  r_int = r_sorted.astype(int)
  delta_r = r_int[1:] - r_int[:-1]
  r_ind = np.where(delta_r)[0]
  # Compute the number of elements in each bin.
  size_per_bin = r_ind[1:] - r_ind[:-1]
  # Finally, compute the average value for each bin.
  f_sorted = f2d.flat[ind]
  f_cumsum = np.cumsum(f_sorted, dtype = float)  # total cumulative sum
  sum_per_bin = f_cumsum[r_ind[1:]] - f_cumsum[r_ind[:-1]]  # cum. sum per bin
  # Use a circular window
  size = min(f2d.shape)
  sum_per_bin = sum_per_bin[: size / 2]
  size_per_bin = size_per_bin[: size / 2]
  # Compute the frequency (in cycles per pixel) corresponding to each bin.
  freq = np.arange(0, size / 2).astype(float) / size
  # Compute the average power for each bin.
  # XXX the average may be significantly more accurate than the sum, as there
  # are many fewer low-frequency locations in the FFT.
  #~ avg_per_bin = sum_per_bin / size_per_bin
  return np.array([freq, sum_per_bin, size_per_bin])
