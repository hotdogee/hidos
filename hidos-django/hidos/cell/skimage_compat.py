"""
The analysis algorithms were written against Python 2.7 and scikit-image
0.12 (2016). These helpers keep their original semantics where newer
versions changed a default or a threshold, so the ported algorithms produce
the same numbers:

* remove_small_objects / remove_small_holes: the old `min_size` removed
  objects strictly *smaller* than it; scikit-image 0.26 replaced it with
  `max_size`, which removes objects smaller than *or equal to* it.
* resize: scikit-image 0.15 switched the default mode from 'constant' to
  'reflect', turned on anti-aliasing when downsampling, and later moved to
  ndimage.zoom; this is the 0.12 implementation.
* prewitt, roberts, sobel, laplace: scikit-image 0.12 set the one pixel
  image border of the edge filters to 0 when no mask was given; newer
  versions keep the (reflect-padded) border values.
* canny: the scikit-image 0.12 implementation (see below).
* gaussian_blur: OpenCV 4 made cv2.GaussianBlur bit-exact (fixed point) for
  8-bit images; OpenCV 3 filtered with the floating point kernel, which
  this reproduces.
* py2_round: Python 2 round() returned a float, rounded halves away from
  zero and passed NaN through; Python 3 rounds halves to even and raises on
  NaN.
"""
import math

import cv2
import numpy as np
from skimage import filters, morphology, transform


def _max_size(min_size):
    # objects with size < min_size  <=>  size <= ceil(min_size) - 1
    return int(math.ceil(min_size)) - 1


def remove_small_objects(ar, min_size=64, connectivity=1):
    """Remove objects with fewer than `min_size` pixels."""
    return morphology.remove_small_objects(ar, max_size=_max_size(min_size), connectivity=connectivity)


def remove_small_holes(ar, min_size=64, connectivity=1):
    """Fill holes with fewer than `min_size` pixels."""
    return morphology.remove_small_holes(ar, max_size=_max_size(min_size), connectivity=connectivity)


def resize(image, output_shape, order=1, mode='constant', cval=0, clip=True, preserve_range=False):
    """
    skimage.transform.resize as implemented in scikit-image 0.12: a warp with
    the affine transform estimated from three corners, no anti-aliasing and
    'constant' padding. (Newer versions use ndimage.zoom, whose rounding
    noise flips the astype(uint8) truncation the algorithms apply to
    resized 0/1 masks.)
    """
    if image.dtype == bool and order != 0:
        # 0.12 interpolated boolean images as floats; 0.26 refuses to
        image = image.astype(np.float64)
    rows, cols = output_shape[0], output_shape[1]
    if len(output_shape) == 3 and (image.ndim == 2 or output_shape[2] != image.shape[2]):
        return transform.resize(image, output_shape, order=order, mode=mode, cval=cval, clip=clip,
                                preserve_range=preserve_range, anti_aliasing=False)
    orig_rows, orig_cols = image.shape[0], image.shape[1]
    row_scale = float(orig_rows) / rows
    col_scale = float(orig_cols) / cols
    if rows == 1 and cols == 1:
        tform = transform.AffineTransform(translation=(orig_cols / 2.0 - 0.5, orig_rows / 2.0 - 0.5))
    else:
        # 3 control points necessary to estimate exact AffineTransform
        src_corners = np.array([[1, 1], [1, rows], [cols, rows]]) - 1
        dst_corners = np.zeros(src_corners.shape, dtype=np.double)
        # take into account that 0th pixel is at position (0.5, 0.5)
        dst_corners[:, 0] = col_scale * (src_corners[:, 0] + 0.5) - 0.5
        dst_corners[:, 1] = row_scale * (src_corners[:, 1] + 0.5) - 0.5
        tform = transform.AffineTransform.from_estimate(src_corners, dst_corners)
    return transform.warp(image, tform, output_shape=output_shape, order=order, mode=mode, cval=cval,
                          clip=clip, preserve_range=preserve_range)


def _mask_filter_result(result, mask):
    if mask is None:
        for axis in range(result.ndim):
            index = [slice(None)] * result.ndim
            index[axis] = 0
            result[tuple(index)] = 0
            index[axis] = -1
            result[tuple(index)] = 0
    return result


def prewitt(image, mask=None):
    return _mask_filter_result(filters.prewitt(image, mask=mask), mask)


def roberts(image, mask=None):
    return _mask_filter_result(filters.roberts(image, mask=mask), mask)


def sobel(image, mask=None):
    return _mask_filter_result(filters.sobel(image, mask=mask), mask)


def laplace(image, ksize=3, mask=None):
    return _mask_filter_result(filters.laplace(image, ksize=ksize, mask=mask), mask)


def gaussian_blur(src, ksize, sigmaX, sigmaY=0):
    """cv2.GaussianBlur as computed by OpenCV 3 (separable float kernel)."""
    kx = cv2.getGaussianKernel(ksize[0], sigmaX)
    ky = cv2.getGaussianKernel(ksize[1], sigmaY or sigmaX)
    return cv2.sepFilter2D(src, -1, kx, ky, borderType=cv2.BORDER_REFLECT_101)


def py2_round(x):
    """round(x) as in Python 2."""
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        return x
    ax = abs(x)
    r = math.floor(ax)
    if ax - r >= 0.5:
        r += 1
    return math.copysign(float(r), x)


# --- canny -------------------------------------------------------------------
# skimage.feature.canny as shipped in scikit-image 0.12 (originally part of
# CellProfiler; Copyright (c) 2003-2009 Massachusetts Institute of Technology,
# Copyright (c) 2009-2011 Broad Institute; BSD license; original author Lee
# Kamentsky). Newer versions convert the image to float before smoothing and
# changed the hysteresis, which moves the detected edges by a few pixels.

def _smooth_with_function_and_mask(image, function, mask):
    bleed_over = function(mask.astype(float))
    masked_image = np.zeros(image.shape, image.dtype)
    masked_image[mask] = image[mask]
    smoothed_image = function(masked_image)
    output_image = smoothed_image / (bleed_over + np.finfo(float).eps)
    return output_image


def canny(image, sigma=1., low_threshold=None, high_threshold=None, mask=None,
          use_quantiles=False):
    """Canny edge detector with the scikit-image 0.12 implementation."""
    import scipy.ndimage as ndi
    from scipy.ndimage import binary_erosion, gaussian_filter, generate_binary_structure, label
    from skimage.util import dtype_limits

    if image.ndim != 2:
        raise ValueError('canny expects a 2-D image')
    if low_threshold is None:
        low_threshold = 0.1 * dtype_limits(image)[1]
    if high_threshold is None:
        high_threshold = 0.2 * dtype_limits(image)[1]
    if mask is None:
        mask = np.ones(image.shape, dtype=bool)

    def fsmooth(x):
        return gaussian_filter(x, sigma, mode='constant')

    smoothed = _smooth_with_function_and_mask(image, fsmooth, mask)
    jsobel = ndi.sobel(smoothed, axis=1)
    isobel = ndi.sobel(smoothed, axis=0)
    abs_isobel = np.abs(isobel)
    abs_jsobel = np.abs(jsobel)
    magnitude = np.hypot(isobel, jsobel)

    # Make the eroded mask. Setting the border value to zero will wipe
    # out the image edges for us.
    s = generate_binary_structure(2, 2)
    eroded_mask = binary_erosion(mask, s, border_value=0)
    eroded_mask = eroded_mask & (magnitude > 0)

    # --------- Find local maxima --------------
    local_maxima = np.zeros(image.shape, bool)
    # 0-45 degrees
    pts_plus = (isobel >= 0) & (jsobel >= 0) & (abs_isobel >= abs_jsobel)
    pts_minus = (isobel <= 0) & (jsobel <= 0) & (abs_isobel >= abs_jsobel)
    pts = pts_plus | pts_minus
    pts = eroded_mask & pts
    c1 = magnitude[1:, :][pts[:-1, :]]
    c2 = magnitude[1:, 1:][pts[:-1, :-1]]
    m = magnitude[pts]
    w = abs_jsobel[pts] / abs_isobel[pts]
    c_plus = c2 * w + c1 * (1 - w) <= m
    c1 = magnitude[:-1, :][pts[1:, :]]
    c2 = magnitude[:-1, :-1][pts[1:, 1:]]
    c_minus = c2 * w + c1 * (1 - w) <= m
    local_maxima[pts] = c_plus & c_minus
    # 45-90 degrees
    pts_plus = (isobel >= 0) & (jsobel >= 0) & (abs_isobel <= abs_jsobel)
    pts_minus = (isobel <= 0) & (jsobel <= 0) & (abs_isobel <= abs_jsobel)
    pts = pts_plus | pts_minus
    pts = eroded_mask & pts
    c1 = magnitude[:, 1:][pts[:, :-1]]
    c2 = magnitude[1:, 1:][pts[:-1, :-1]]
    m = magnitude[pts]
    w = abs_isobel[pts] / abs_jsobel[pts]
    c_plus = c2 * w + c1 * (1 - w) <= m
    c1 = magnitude[:, :-1][pts[:, 1:]]
    c2 = magnitude[:-1, :-1][pts[1:, 1:]]
    c_minus = c2 * w + c1 * (1 - w) <= m
    local_maxima[pts] = c_plus & c_minus
    # 90-135 degrees
    pts_plus = (isobel <= 0) & (jsobel >= 0) & (abs_isobel <= abs_jsobel)
    pts_minus = (isobel >= 0) & (jsobel <= 0) & (abs_isobel <= abs_jsobel)
    pts = pts_plus | pts_minus
    pts = eroded_mask & pts
    c1a = magnitude[:, 1:][pts[:, :-1]]
    c2a = magnitude[:-1, 1:][pts[1:, :-1]]
    m = magnitude[pts]
    w = abs_isobel[pts] / abs_jsobel[pts]
    c_plus = c2a * w + c1a * (1.0 - w) <= m
    c1 = magnitude[:, :-1][pts[:, 1:]]
    c2 = magnitude[1:, :-1][pts[:-1, 1:]]
    c_minus = c2 * w + c1 * (1.0 - w) <= m
    local_maxima[pts] = c_plus & c_minus
    # 135-180 degrees
    pts_plus = (isobel <= 0) & (jsobel >= 0) & (abs_isobel >= abs_jsobel)
    pts_minus = (isobel >= 0) & (jsobel <= 0) & (abs_isobel >= abs_jsobel)
    pts = pts_plus | pts_minus
    pts = eroded_mask & pts
    c1 = magnitude[:-1, :][pts[1:, :]]
    c2 = magnitude[:-1, 1:][pts[1:, :-1]]
    m = magnitude[pts]
    w = abs_jsobel[pts] / abs_isobel[pts]
    c_plus = c2 * w + c1 * (1 - w) <= m
    c1 = magnitude[1:, :][pts[:-1, :]]
    c2 = magnitude[1:, :-1][pts[:-1, 1:]]
    c_minus = c2 * w + c1 * (1 - w) <= m
    local_maxima[pts] = c_plus & c_minus

    # ---- If use_quantiles is set then calculate the thresholds to use
    if use_quantiles:
        if high_threshold > 1.0 or low_threshold > 1.0:
            raise ValueError("Quantile thresholds must not be > 1.0")
        if high_threshold < 0.0 or low_threshold < 0.0:
            raise ValueError("Quantile thresholds must not be < 0.0")
        high_threshold = np.percentile(magnitude, 100.0 * high_threshold)
        low_threshold = np.percentile(magnitude, 100.0 * low_threshold)

    # ---- Create two masks at the two thresholds.
    high_mask = local_maxima & (magnitude >= high_threshold)
    low_mask = local_maxima & (magnitude >= low_threshold)

    # Segment the low-mask, then only keep low-segments that have
    # some high_mask component in them
    strel = np.ones((3, 3), bool)
    labels, count = label(low_mask, strel)
    if count == 0:
        return low_mask

    sums = np.array(ndi.sum(high_mask, labels, np.arange(count, dtype=np.int32) + 1), ndmin=1)
    good_label = np.zeros((count + 1,), bool)
    good_label[1:] = sums > 0
    output_mask = good_label[labels]
    return output_mask
