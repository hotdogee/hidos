"""
Python 3 port of the subset of pymorph 0.96 used by the Cell Cloud
analysis algorithms (cella1, cellc2 and celln1).

pymorph (https://github.com/luispedro/pymorph) is archived upstream and its
only PyPI release (0.96, 2010) is Python 2 only, so the functions the
algorithms call -- label, blob, dilate, endpoints, se2hmt, sedisk, supcanon,
thin, union, overlay -- and their internal helpers are copied here verbatim from
pymorph/mmorph.py, changed only as needed for Python 3 and NumPy 2:
xrange -> range, string.lower/upper -> str methods, numpy.bool -> bool,
numpy.product -> numpy.prod, `x != None` -> `x is not None` (NumPy now
compares arrays to None elementwise), int() around float slice indices in
pad4n (NumPy 1.x truncated them), and Python 3 raise/print syntax.

Copyright 2003, Roberto A. Lotufo, UNICAMP-University of Campinas;
CenPRA-Renato Archer Research Center, Rubens C. Machado.
Copyright 2008-2010, Luis Pedro Coelho <lpc@cmu.edu>
pymorph is distributed under the BSD license terms.
"""
# ruff: noqa


def limits(f):
    """
    y = limits(f)

    Get the possible minimum and maximum of an image.
    The possible minimum and the possible maximum of an image depend
    on its data type. These values are important to compute many
    morphological operators (for instance, negate of an image). The
    output is a vector, where the first element is the possible
    minimum and the second, the possible maximum.

    Parameters
    ----------
    f : Unsigned gray-scale (uint8 or uint16), signed (int32) or binary image.

    Returns
    -------
    y : Two element vector
        the first element is the infimum, the second, the supremum.
    """
    from numpy import array, uint8, uint16, int32, int64
    code = f.dtype
    if code == bool: return array([0,1])
    if code == uint8: return array([0,255])
    if code == uint16: return array([0,65535])
    if code == int32: return array([-2147483647,2147483647])
    if code == int64: return array([-2**63,2**63-1])

    raise ValueError('pymorph.limits: does not accept this typecode: %s' % code)


def overlay(X, red=None, green=None, blue=None, magenta=None, yellow=None, cyan=None):
    """
    Y = overlay(X, red=None, green=None, blue=None, magenta=None, yellow=None, cyan=None)

    Apply binary overlays as colour layers on a binary or gray-scale image

    Parameters
    ----------
    X :  Gray-scale (uint8 or uint16) or binary image.
    red : Red overlay, binary image(default: None)
    green : Green overlay, binary image (default: None)
    blue : blue overlay, binary image (default: None)
    magenta : magenta overlay, binary image (default: None)
    yellow : yellow overlay, binary image (default: None)
    cyan : cyan overlay, binary image (default: None)

    Returns
    -------
    Y : Colour image (in HxWx3 format)
    """
    from numpy import dstack
    if isbinary(X): X = gray(X,'uint8')
    r = X
    g = X
    b = X
    if red is not None: # red 1 0 0
      red = gray(asbinary(red),'uint8')
      r = union(r,red)
      g = intersec(g,neg(red))
      b = intersec(b,neg(red))
    if green is not None: # green 0 1 0
      green = gray(asbinary(green),'uint8')
      r = intersec(r,neg(green))
      g = union(g,green)
      b = intersec(b,neg(green))
    if blue is not None: # blue 0 0 1
      blue = gray(asbinary(blue),'uint8')
      r = intersec(r,neg(blue))
      g = intersec(g,neg(blue))
      b = union(b,blue)
    if magenta is not None: # magenta 1 0 1
      magenta = gray(magenta,'uint8')
      r = union(r,magenta)
      g = intersec(g,neg(magenta))
      b = union(b,magenta)
    if yellow is not None: # yellow 1 1 0
      #assert isbinary(yellow),'yellow must be binary overlay'
      yellow = gray(asbinary(yellow),'uint8')
      r = union(r,yellow)
      g = union(g,yellow)
      b = intersec(b,neg(yellow))
    if cyan is not None: # cyan 0 1 1
      #assert isbinary(cyan),'cyan must be binary overlay'
      cyan = gray(asbinary(cyan),'uint8')
      r = intersec(r,neg(cyan))
      g = union(g,cyan)
      b = union(b,cyan)
    return dstack((r,g,b))


def label(f, Bc=None):
    """
    y = label(f, Bc={3x3 cross})

    Label a binary image.

    `label` creates the image `y` by labeling the connect components
    of a binary image `f`, according to the connectivity defined by
    the structuring element `Bc`. The background pixels (with value
    0) are not labeled. The maximum label value in the output image
    gives the number of its connected components.

    Parameters
    ----------
    f :  Binary image.
    Bc : Connectivity (default: 3x3 cross)

    Returns
    -------
    y : Image of same size as `f`.
        If number of labels is less than 65535, the data type
        is uint16, otherwise it is int32.
    """
    if Bc is None: Bc = secross()
    if not isbinary(f):
        f = (f > 0)
    f = pad4n(f, Bc, 0)
    neighbours = se2flatidx(f,Bc)
    labeled = f * 0
    f = f.ravel()
    labeledflat=labeled.ravel()
    label = 1
    queue = []
    for i in range(f.size):
        if f[i] and labeledflat[i] == 0:
            labeledflat[i]=label
            queue=[i+bi for bi in neighbours]
            while queue:
                ni=queue.pop()
                if f[ni] and labeledflat[ni] == 0:
                    labeledflat[ni]=label
                    for n in neighbours+ni:
                        queue.append(n)
            label += 1
    return labeled[1:-1,1:-1] # revert the pad4n() call above


def neg(f):
    """
    y = neg(f)

    Negate an image.

    `neg` returns an image `y` that is the negation (i.e., inverse or
    involution) of the image `f`. In the binary case, `y` is the
    complement of `f`.

    Parameters
    ----------
    f : Unsigned gray-scale (uint8 or uint16), signed (int32) or binary image.

    Returns
    -------
    y : ndarray of same shape and dtype as `f`
    """

    y = limits(f)[0] + limits(f)[1] - f
    return y.astype(f.dtype)


def binary(f, k=1):
    """
    y = binary(f, k=1)

    Convert a gray-scale image into a binary image

    `binary` converts a gray-scale image `f` into a binary image `y` by
    a threshold rule. A pixel in `y` has the value 1 if and only if
    the corresponding pixel in `f` has a value greater or equal to `k`.

    Parameters
    ----------
    f :  Unsigned gray-scale (uint8 or uint16), signed (int32) or binary image.
    k : integer, optional
        Threshold used inclusively (default: 1)

    Returns
    -------
    y : Binary image.
    """
    from numpy import asanyarray
    f = asanyarray(f)
    return (f >= k)


def blob(f, measurement, output="image"):
    """
    y = blob(f, measurement, output="image")

    Blob measurements from a labeled image.

    Take measurements from the labeled image f.

    The measurements are:

    - area,
    - centroid,
    - bounding rectangle.

    `output` controls the output format:

    image
        the result is an image
    data
        the result is a double column vector with the measurement for each
        blob.

    The region with label zero is not measured as it is normally
    the background. The measurement of region with label 1 appears
    at the first row of the output.

    Parameters
    ----------
    f :           Gray-scale (uint8 or uint16) image. Labeled image.
    measurement : Measurement. One of ('area', 'centroid', 'boundingbox').
    output : {'image' [default], 'data'}, optional
            Output format: if 'image', returns a binary image; if 'data',
            returns a vector of measurements

    Returns
    -------
    y : Gray-scale (uint8 or uint16) or binary image.
    """
    import numpy
    from numpy import newaxis, ravel, zeros, sum, nonzero, array, asanyarray

    measurement = measurement.lower()
    output      = output.lower()
    if len(f.shape) == 1: f = f[newaxis,:]
    assert measurement in ('area', 'centroid', 'boundingbox'), 'pymorph.blob: Unknown measurement type \'%s\'' % measurement
    if output == 'data':
        y = []
    elif measurement == 'centroid':
        y = zeros(f.shape,bool)
    else:
        y = zeros(f.shape,numpy.int32)
    for obj_id in range(f.max()):
        blob = (f == (obj_id+1))
        if measurement == 'area':
            area = blob.sum()
            if output == 'data': y.append(area)
            else               : y += area*blob
        elif measurement == 'centroid':
            indy, indx  = nonzero(blob)
            cy = sum(indy) // len(indy)
            cx = sum(indx) // len(indx)
            if output == 'data': y.append( (cy, cx) )
            else               : y[cy, cx] = 1
        elif measurement == 'boundingbox':
            col, = nonzero(blob.any(0))
            row, = nonzero(blob.any(1))
            if output == 'data': y.append([col[0],row[0],col[-1]+1,row[-1]+1])
            else:
                y[row[0]:row[-1], col[0]] = 1
                y[row[0]:row[-1],col[-1]] = 1
                y[row[0], col[0]:col[-1]] = 1
                y[row[-1],col[0]:col[-1]] = 1
    return asanyarray(y)


def dilate(f, B=None):
    """
    y = dilate(f, B={3x3 cross})

    Dilate an image by a structuring element.

    `dilate` performs the dilation of image `f` by the structuring
    element `B`. Dilation is a neighbourhood operator that compares
    locally `B` with `f`, according to an intersection rule. Since
    Dilation is a fundamental operator to the construction of all
    other morphological operators, it is also called an elementary
    operator of Mathematical Morphology. When f is a gray-scale
    image, `B` may be a flat or non-flat structuring element.

    Parameters
    ----------
    f : Gray-scale (uint8 or uint16) or binary image.
    B : Structuring element (default: 3x3 cross).

    Returns
    -------
    y: Same type as `f`
    """
    from numpy import maximum, newaxis, ones, int32
    if B is None: B = secross()
    if len(f.shape) == 1: f = f[newaxis,:]
    if isbinary(f): B = asbinary(B)
    h,w = f.shape
    x,v = mat2set(B)
    if len(x)==0:
        y = (ones((h,w),int32) * limits(f)[0]).astype(f.dtype)
    else:
        if isbinary(v):
            v = intersec(gray(v,'int32'),0)
        mh,mw = max(abs(x)[:,0]),max(abs(x)[:,1])
        y = (ones((h+2*mh,w+2*mw),int32) * limits(f)[0]).astype(f.dtype)
        for i in range(x.shape[0]):
            if v[i] > -2147483647:
                y[mh+x[i,0]:mh+x[i,0]+h, mw+x[i,1]:mw+x[i,1]+w] = maximum(
                    y[mh+x[i,0]:mh+x[i,0]+h, mw+x[i,1]:mw+x[i,1]+w], add4dilate(f,v[i]))
        y = y[mh:mh+h, mw:mw+w]
    return y


def endpoints(option="loop"):
    """
    iab = endpoints(option="loop")

    Interval to detect end-points.

    `endpoints` creates an interval that is useful to detect
    end-points of curves (i.e., one pixel thick connected
    components) in binary images. It can be used to prune skeletons
    and to mark objects transforming them in a single pixel or
    closed loops if they have holes. There are two options
    available: 'loop', deletes all points but preserves loops if used
    in thin ; 'homotopic', deletes all points but preserves the last
    single point or loops.

    Parameters
    ----------
    option : {'loop' [default], 'homotopic'}
        type of interval

    Returns
    -------
    Iab : Interval
    """
    option = option.lower()
    if option == 'loop':
        return se2hmt(binary([[0,0,0],
                              [0,1,0],
                              [0,0,0]]),

                      binary([[0,0,0],
                              [1,0,1],
                              [1,1,1]]))
    elif option == 'homotopic':
        return se2hmt(binary([[0,1,0],
                              [0,1,0],
                              [0,0,0]]),

                      binary([[0,0,0],
                              [1,0,1],
                              [1,1,1]]))
    from warnings import warn
    warn('pymorph.endpoints: Did not understand argument "%s".' % option)
    return None


def erode(f, b=None):
    """
    y = erode(f, b={3x3 cross})

    Erode an image by a structuring element.

    `erode` performs the erosion of the image `f` by the structuring
    element `b`. Erosion is a neighbourhood operator that compairs
    locally `b` with `f`, according to an inclusion rule. Since erosion
    is a fundamental operator to the construction of all other
    morphological operators, it is called an elementary
    operator of Mathematical Morphology. When `f` is a gray-scale
    image, `b` may be a flat or non-flat structuring element.

    Parameters
    ----------
    f : Gray-scale (uint8 or uint16) or binary image.
    b : Structuring element (Default: 3x3 elementary cross).

    Returns
    -------
    y : Image

    See Also
    --------
    mahotas.erode : implementation of binary erosion
    scipy.ndimage.grey_erosion : implementation of grey erosion
    """

    if b is None: b = secross()
    return neg(dilate(neg(f),sereflect(b)))


def gray(f, dtype="uint8", k=None):
    """
    y = gray(f, dtype="uint8", k=None)

    Convert a binary image into a gray-scale image.

    `gray` converts a binary image into a gray-scale image of a
    specified data type. The value `k` is assigned to the 1 pixels of
    `f`, while the `0` pixels are assigned to the minimum value
    associated to the specified data type.

    Parameters
    ----------
    f :      Binary image.
    dtype :  { 'uint8' [default], 'uint16', 'int32' }
    k : scalar, optional
        Pixel value to assign to `True` pixels (default: max value for `dtype`).

    Returns
    -------
    y : Unsigned gray-scale (uint8 or uint16), signed (int32) or binary image.
    """
    from numpy import array
    if k is None: k = maxleveltype(dtype)
    if type(f) is list: f = binary(f)
    assert isbinary(f), 'f must be binary'
    if   dtype == 'uint8' : y = to_uint8(f*k)
    elif dtype == 'uint16': y = to_uint16(f*k)
    elif dtype == 'int32' : y = to_int32(f*k) - to_int32(neg(f)*maxleveltype(dtype))
    else:
        assert 0, 'pymorph.gray: type not supported: %s' % dtype
    return y


def homothin():
    """
    Iab = homothin()

    Interval for homotopic thinning.

    `homothin` creates an interval that is useful for the homotopic
    (i.e., that conserves the relation between objects and holes)
    thinning of binary images.

    Returns
    -------
    Iab : Interval
    """
    return se2hmt(binary([[0,0,0],
                          [0,1,0],
                          [1,1,1]]),

                   binary([[1,1,1],
                           [0,0,0],
                           [0,0,0]]))


def interot(Iab, theta=45, direction="clockwise"):
    """
    Irot = interot(Iab, theta=45, direction="clockwise")

    Rotate an interval

    `interot` rotates the interval `Iab` by `theta`.

    Parameters
    ----------
    Iab :       Interval
    theta :     Degrees of rotation. Should be a multiple of 45 degrees. If not,
                   the rotation is approximate (default: 45).
    direction : { 'clockwise' [default], 'anti-clockwise' }

    Returns
    -------
    Irot : Interval

    Examples
    --------
    
    ::

        b1 = endpoints()
        b2 = interot(b1)
        print(intershow(b1))
        print(intershow(b2))

    """

    direction = direction.lower()
    A,Bc = Iab
    if direction != 'clockwise':
        theta = 360 - theta
    Irot = se2hmt(serot(A, theta),
                    serot(Bc,theta))
    return Irot


def intersec(f1, f2, f3=None, f4=None, f5=None):
    """
    y = intersec(f1, f2, f3=None, f4=None, f5=None)

    Intersection of images.

    `intersec` creates the image `y` by taking the pixelwise minimum
    between the images `f1`, `f2`, `f3`, `f4`, and `f5` . When `f1`,
    `f2`, `f3`, `f4`, and f5 are binary images, `y` is the intersection
    of them.

    Parameters
    ----------
    f1 : Image (gray or binary) or constant.
    f2 : Image (gray or binary) or constant.
    f3 : Image (gray or binary) or constant, optional.
    f4 : Image (gray or binary) or constant, optional.
    f5 : Image (gray or binary) or constant, optional.

    Returns
    -------
    y : Image
    """
    """
    - Examples
      #
      #   example 1
      #
      f=to_uint8([255,  255,    0,   10,    0,   255,   250])
      g=to_uint8([ 0,    40,   80,   140,  250,    10,    30])
      print(intersec(f, g))
      print(intersec(f, 0))
      #
      #   example 2
      #
      a = readgray('form-ok.tif')
      b = readgray('form-1.tif')
      c = intersec(a,b)
      show(a)
      show(b)
      show(c)
      #
      #   example 3
      #
      d = readgray('tplayer1.tif')
      e = readgray('tplayer2.tif')
      f = readgray('tplayer3.tif')
      g = intersec(d,e,f)
      show(d)
      show(e)
      show(f)
      show(g)
    """
# Should this be intersect(f0, f1, *args) and take an arbitrary nr of inputs?
    from numpy import minimum

    y = minimum(f1,f2)
    if f3 is not None: y = minimum(y,f3)
    if f4 is not None: y = minimum(y,f4)
    if f5 is not None: y = minimum(y,f5)
    return y.astype(f1.dtype)


def intershow(Iab):
    """
    s = intershow(Iab)

    Visualize an interval.

    `intershow` creates a representation for an interval using `0`, `1`
    and `.` (don't care).

    Parameters
    ----------
    Iab : Interval

    Returns
    -------
    s : string representation of the interval.

    Examples
    --------
    ::

        print(intershow(homothick()))

    prints out

    ::

        0 0 0
        . 0 .
        0 0 0
    """
    from numpy import array, reshape, choose

    assert (type(Iab) is tuple) and (len(Iab) == 2),'pymorph.intershow: not proper format of hit-or-miss template'
    A,B = Iab
    s = ''
    for y in range(A.shape[0]):
        for x in range(A.shape[1]):
            if A[y,x]:
                s += '1 '
            elif B[y,x]:
                s += '0 '
            else:
                s += '. '
        s += '\n'
    return s


def isbinary(f):
    """
    is_b = isbinary(f)

    Check for binary image

    `isbinary` returns True if the datatype of the input image is
    binary. A binary image has just the values `0` and `1`.

    Parameters
    ----------
    f : Image

    Returns
    -------
    is_b : bool
        Whether `f` is a binary image
    """
    return f.dtype == bool


def asbinary(f):
    """
    fbin = asbinary(f)

    Transforms f into a binary image

    Parameters
    ----------
    f : image of any type, consisting only of 0s and 1s.

    Returns
    -------
      fbin : binary image
    """
    import numpy
    if isbinary(f): return f
    assert ( (f == 0) | (f == 1) ).sum() == f.size, 'pymorph.asbinary: f has values that are not 0 or 1.'
    return (f != 0)


def isequal(f1, f2):
    """
    r_eq = isequal(f1, f2)

    Check if two images are equal

    `isequal` compares the images `f1` and f2 and returns `True`, if
    `f1 and `f2` have the same size and `f1(x) == f2(x)`, for all pixel `x`;
    otherwise, returns `False`.

    Parameters
    ----------
    f1 :  Unsigned gray-scale (uint8 or uint16), signed (int32) or binary image.
    f2 :  Unsigned gray-scale (uint8 or uint16), signed (int32) or binary image.

    Returns
    -------
    r_eq : Boolean
        Whether the two images are equal
    """
    import numpy
    if f1.shape != f2.shape:
        return False
    return numpy.all(f1 == f2)


def se2hmt(A, Bc):
    """
    Iab = se2hmt(A, Bc)

    Create a Hit-or-Miss Template (or interval) from a pair of
    structuring elements.

    `se2hmt` creates the Hit-or-Miss Template (HMT), also called
    interval `[A,Bc]` from the structuring elements `A` and `Bc` such that
    `A` is included in the complement of `Bc` . The only difference
    between this function and `se2interval` is that here the second
    structuring element is the complement of the one used in the
    other function. The advantage of this function over
    `se2interval` is that this one is more flexible in the use of
    the structuring elements as they are not required to have the
    same size.

    Parameters
    ----------
    A :  Structuring Element Left extremity.
    Bc : Structuring Element Complement of the right extremity.

    Returns
    -------
    Iab : Interval
    """
    return A, Bc


def se2flatidx(f,Bc):
    """
    Bi = se2flatidx(f,Bc)

    Transforms the Bc structuring element into an array of indices so that
    f.flat[Bi[i]] corresponds to the i-th element where Bc is true

    Equivalent of::

        g = zeros(f.shape)
        h,w=Bc.shape
        g[:h,:w]=Bc
        Bi, = where(g.ravel())

    This is useful for implementing many functions. See the implementation of
    `label()` for an example.

    Parameters
    ----------
    f : image
    Bc : structuring element

    Returns
    -------
    Bi : array of indice offsets.
    """
    from numpy import array, where
    h,w=Bc.shape
    h //= 2
    w //= 2
    Bi=[]
    for i,j in zip(*where(Bc)):
        Bi.append( (j-w)+(i-h)*f.shape[1] )
    return array(Bi)


def sebox(r=1):
    """
    B = sebox(r=1)

    Create a box structuring element.

    `sebox` creates the structuring element B formed by r successive
    Minkowski additions of the elementary square (i.e., the 3x3
    square centered at the origin) with itself. If `R=0`, `B` is the
    unitary set that contains the origin. If `R=1`, `B` is the
    elementary square itself.

    Parameters
    ----------
    r : integer, optional
        size of box (default: 1)

    Returns
    -------
    B : Structuring Element
    """

    return sesum(binary([[1,1,1],
                         [1,1,1],
                         [1,1,1]]),
                 r)


def secross(r=1):
    """
    B = secross(r=1)

    Diamond structuring element and elementary 3x3 cross.

    `secross` creates the structuring element `B` formed by `r`
    successive Minkowski additions of the elementary cross (i.e.,
    the 3x3 cross centered at the origin) with itself. If `r=0`, `B` is
    the unitary set that contains the origin. If `r=1` (the default),
    `B` is the elementary cross itself.

    Parameters
    ----------
    r : integer, optional
        radius (default: 1)

    Returns
    -------
    B : Structuring Element
    """
    return sesum(binary([[0,1,0],
                         [1,1,1],
                         [0,1,0]]),
                 r)


def sedisk(r=3, dim=2, metric="euclidean", flat=True, h=0):
    """
    B = sedisk(r=3, dim=2, metric="euclidean", flat=True, h=0)

    Create a disk or a semi-sphere structuring element.

    `sedisk` creates a flat structuring element B that is disk under
    the metric metric , centered at the origin and with radius r or
    a non-flat structuring element that is a semi-sphere under the
    metric metric, centered at (0, h) and with radius r . this
    structuring element can be created on the 1D, 2D or 3D space.

    Parameters
    ----------
    r :        Non-negative integer. Disk radius (default: 3)
    dim : {1, 2 [default], 3}
        dimension
    metric : {'euclidean' [default], 'city-block', 'octagon', 'chessboard' }
    flat : boolean, optional
        default: True
    h : double, optional
        elevation of the center of the semi-sphere (default: 0).

    Returns
    -------
    B : Structuring Element
    """
    from numpy import resize, transpose, arange
    from numpy import sqrt, arange, transpose, maximum

    metric = metric.lower()
    assert dim== 2, 'pymorph.sedisk: Supports only 2D structuring elements'
    if flat: y = binary([[1]])
    else:    y = to_int32([[h]])
    if r == 0: return y
    if metric == 'city-block':
        if flat:
            b = secross(1)
        else:
            b = to_int32([[-2147483647, 0,-2147483647],
                          [          0, 1,          0],
                          [-2147483647, 0,-2147483647]])
        return sedilate(y,sesum(b,r))
    elif metric == 'chessboard':
        if flat:
            b = sebox(1)
        else:
            b = to_int32([[1,1,1],
                          [1,1,1],
                          [1,1,1]])
        return sedilate(y,sesum(b,r))
    elif metric == 'octagon':
        if flat:
            b1,b2 = sebox(1),secross(1)
        else:
            b1 = to_int32([
                    [1,1,1],
                    [1,1,1],
                    [1,1,1]])
            b2 = to_int32([
                    [-2147483647, 0, -2147483647],
                    [          0, 1,           0],
                    [-2147483647, 0, -2147483647]])
        if r == 1:
            return b1
        return sedilate(sedilate(y,sesum(b1,r//2)), sesum(b2,(r+1)//2))
    elif metric == 'euclidean':
        v = arange(-r,r+1)
        x = resize(v, (len(v), len(v)))
        y = transpose(x)
        Be = binary(sqrt(x*x + y*y) <= (r+0.5))
        if flat:
            return Be
        be = h + to_int32( sqrt( maximum((r+0.5)*(r+0.5) - (x*x) - (y*y),0)))
        be = intersec(gray(Be,'int32'),be)
        return be
    else:
        assert False,'Non valid metric'
    return B


def serot(b, theta=45, direction="clockwise"):
    """
    brot = serot(b, theta=45, direction="clockwise")

    Rotate a structuring element.
    `serot` rotates structuring element `b` by `theta` degrees.

    Parameters
    ----------
    B :       Structuring Element
    theta :   Degrees of rotation. Should be a multiple of 45 degrees. If not,
                the rotation is approximate (default: 45).
    direction : { 'clockwise' [default], 'anti-clockwise' }

    Returns
    -------
    brot : structuring element
    """
    from numpy import array, transpose, concatenate
    from numpy import cos, sin, pi

    direction = direction.lower()
    if direction == "anti-clockwise":
       theta = -theta
    theta = pi * theta/180.
    ct = cos(theta)
    st = sin(theta)
    y,v = mat2set(b)
    if len(y)==0: return binary([0])
    x0 = y[:,1] * cos(theta) - y[:,0] * sin(theta)
    x1 = y[:,1] * sin(theta) + y[:,0] * cos(theta)
    x0 = to_int32((x0 +0.5)*(x0>=0) + (x0-0.5)*(x0<0))
    x1 = to_int32((x1 +0.5)*(x1>=0) + (x1-0.5)*(x1<0))
    x = transpose(array([transpose(x1),transpose(x0)]))
    brot = set2mat((x,v))
    return brot


def seshow(b, option="normal"):
    """
    y = seshow(b, option="NORMAL")

    Display a structuring element as an image.

    `seshow` used with the option 'expand' generates an image `y` that
    is a suitable graphical representation of the structuring
    element `b`. This function is useful to convert a structuring
    element to an image. The origin of the structuring element is at
    the center of the image. If `b` is flat, y is binary, otherwise, y
    is signed `int32 image. When using the option 'non-flat', the
    output `y` is always a signed `int32` image.

    Parameters
    ----------
    b :      Structuring element
    option : { 'normal' [default], 'expand', 'non-flat' }
        Mode

    Returns
    -------
    y : Gray-scale (uint8 or uint16) or binary image.
    """

    option = option.upper()
    if option=='NON-FLAT':
        y = to_int32([0])
        if isbinary(b):
            b = intersec(gray(b,'int32'),0)
    elif option=='NORMAL':
        if isbinary(b):
            y = binary([1])
        else:
           y = to_int32([0])
    elif option=='EXPAND':
        assert isbinary(b), 'pymorph.seshow: \'expand\' option is only available with flat SE'
        y = sedilate(binary([1]),b)
        b1 = (y>=0)
        b0 = erode(y,b)
        return bshow(b1,y,b0)
    else:
        assert False, 'pymorph.seshow: not a valid flag: NORMAL, EXPAND or NON-FLAT'
    return sedilate(y,b)


def sesum(B=None, N=1):
    """
    Bn = sesum(B=None, N=1)

    N-1 iterative Minkowski additions

    `sesum` creates the structuring element `Bn` from `N - 1` iterative
    Minkowski additions with the structuring element `B`.

    Parameters
    ----------
    B : Structuring element (Default: 3x3 elementary cross).
    N : Non-negative integer. Default: 1.

    Returns
    -------
    Bn : Structuring Element
    """

    if B is None: B = secross()
    if N==0:
        if isbinary(B): return binary([[1]])
        else:           return to_int32([[0]]) # identity
    NB = B
    for i in range(N-1):
        NB = sedilate(NB,B)
    return NB


def setrans(Bi, t):
    """
    Bo = setrans(Bi, t)

    Translate a structuring element

    setrans translates a structuring element by a specific value.

    Parameters
    ----------
    Bi : Structuring Element
    t : translation amount

    Returns
    -------
    Bo : Structuring element of same type as `Bi`
    """

    x,v = mat2set(Bi)
    Bo = set2mat((x+t,v))
    return Bo.astype(Bi.dtype)


def sereflect(Bi):
    """
    Bo = sereflect(Bi)

    Reflect a structuring element

    `sereflect` reflects a structuring element about the origin

    Parameters
    ----------
    Bi : Structuring Element

    Returns
    -------
    Bo : Structuring element of same type as `Bi`
    """
    return Bi[::-1, ::-1]


def sedilate(B1, B2):
    """
    Bo = sedilate(B1, B2)

    Dilate one structuring element by another

    `sedilate` dilates an structuring element by another. The main
    difference between this dilation and `dilate` is that the dilation
    between structuring elements are not bounded, returning another
    structuring element usually larger than anyone of them. This
    gives the composition of the two structuring elements by
    Minkowski addition.

    Parameters
    ----------
    B1 : Structuring Element
    B2 : Structuring Element

    Returns
    -------
    Bo: Structuring Element
    """
    from numpy import newaxis, array, int32

    assert (isbinary(B1) or (B1.dtype == int32)) and (isbinary(B2) or B2.dtype == int32), 'pymorph.sedilate: s.e. must be binary or int32'
    if len(B1.shape) == 1: B1 = B1[newaxis,:]
    if len(B2.shape) == 1: B2 = B2[newaxis,:]
    if B1.dtype==int32 or B2.dtype == int32:
       Bo = to_int32([limits(to_int32([0]))[0]])
       if isbinary(B1):
          B1 = gray(B1,'int32',0)
       if isbinary(B2):
          B2 = gray(B2,'int32',0)
    else:
       Bo = binary([0])
    x,v = mat2set(B2)
    if len(x):
        for i in range(x.shape[0]):
            s = add4dilate(B1,v[i])
            st= setrans(s,x[i])
            Bo = seunion(Bo,st)
    return Bo


def seunion(B1, B2):
    """
    B = seunion(B1, B2)

    Union of structuring elements

    `seunion` creates a structuring element from the union of two
    structuring elements.

    Parameters
    ----------
    B1 : Structuring element
    B2 : Structuring element

    Returns
    -------
    B : structure element
        union of B1 and B2
    """
    from numpy import maximum, ones, asarray, newaxis, int32

    assert B1.dtype == B2.dtype, 'Cannot have different datatypes:'
    type1 = B1.dtype
    if len(B1) == 0: return B2
    if len(B1.shape) == 1: B1 = B1[newaxis,:]
    if len(B2.shape) == 1: B2 = B2[newaxis,:]
    if B1.shape != B2.shape:
        inf = limits(B1)[0]
        h1,w1 = B1.shape
        h2,w2 = B2.shape
        H,W = max(h1,h2),max(w1,w2)
        Hc,Wc = (H-1)//2,(W-1)//2    # center
        BB1,BB2 = asarray(B1),asarray(B2)
        B1, B2  = inf * ones((H,W),int32), inf *ones((H,W),int32)
        dh1s , dh1e = (h1-1)//2 , (h1-1)//2 + (h1+1)%2 # deal with even and odd dimensions
        dw1s , dw1e = (w1-1)//2 , (w1-1)//2 + (w1+1)%2
        dh2s , dh2e = (h2-1)//2 , (h2-1)//2 + (h2+1)%2
        dw2s , dw2e = (w2-1)//2 , (w2-1)//2 + (w2+1)%2
        B1[ Hc-dh1s : Hc+dh1e+1  ,  Wc-dw1s : Wc+dw1e+1 ] = BB1
        B2[ Hc-dh2s : Hc+dh2e+1  ,  Wc-dw2s : Wc+dw2e+1 ] = BB2
    B = maximum(B1,B2).astype(type1)
    return B


def subm(f1, f2):
    """
    y = subm(f1, f2)

    Subtraction of two images, with saturation.

    `subm` creates the image `y` by pixelwise subtraction of the image
    `f2` from the image `f1`. When the subtraction of the values of two
    pixels is negative, 0 is taken as the result of the subtraction.
    When `f1` and `f2` are binary images, `y` represents the set
    subtraction of `f2` from `f1`.

    Parameters
    ----------
    f1 : Unsigned gray-scale (uint8 or uint16), signed (int32) or binary image.
    f2 : Unsigned gray-scale (uint8 or uint16), signed (int32) or binary image. Or constant.

    Returns
    -------
    y : ndarray of same shape and dtype as `f1`

    Examples
    --------

    ::

        f = to_uint8([255,   255,    0,   10,   20,   10,    0,   255,  255])
        g = to_uint8([10,     20,   30,   40,   50,   40,   30,    20,    10])
        print(subm(f, g))
        print(subm(f, 100))
        print(subm(100, f))

    ::

        a = readgray('boxdrill-C.tif')
        b = readgray('boxdrill-B.tif')
        c = subm(a,b)
        show(a)
        show(b)
        show(c)
    """
    from numpy import array, clip

    if type(f2) is array:
        if f1.dtype != f2.dtype:
            raise TypeError('pymorph.subm(): arguments cannot have different datatypes')
    bottom,top = limits(f1)
    y = clip(f1.astype('d') - f2, bottom, top)
    return y.astype(f1.dtype)


def supcanon(f, Iab, theta=45, direction="clockwise"):
    """
    y = supcanon(f, Iab, theta=45, direction="clockwise")

    Union of sup-generating or hit-miss operators.

    `supcanon` creates the image `y` by computing the union of
    transformations of the image `f` by sup-generating operators.
    These hit-miss operators are characterized by rotations (in the
    clockwise or anti-clockwise direction) of `theta` degrees of the
    interval `Iab`.

    Parameters
    ----------
    f : Binary image.
    Iab : Interval
    theta : {45 [default], 90, 180 }
        Angle of rotation in degrees.
    direction : {'clockwise' [default], 'anti-clockwise'}
        Direction of rotation

    Returns
    ------
    y : Binary image.
    """
    y = intersec(f,0)
    for t in range(0,360,theta):
        Irot = interot(Iab, t, direction)
        y = union(y, supgen(f, Irot))
    return y


def supgen(f, interval):
    """
    y = supgen(f, interval)

    Sup-generating (hit-miss).

    `supgen` creates the binary image `y` by computing the transformation of
    the image f by the sup-generating operator characterized by the interval
    `Iab`. The sup-generating operator is just a relaxed template matching,
    where the criterion to keep a shape is that it be inside the interval
    `Iab`. Note that we have the classical template matching when `a==b`. Note
    also that the sup-generating operator is equivalent to the classical
    hit-miss operator.

    Parameters
    ----------
    f :        Binary image.
    interval : Interval

    Returns
    -------
    y : Binary image.
    """
    """
        - Examples
            #
            #   example 1
            #
            f=binary([
               [0,0,1,0,0,1,1],
               [0,1,0,0,1,0,0],
               [0,0,0,1,1,0,0]])
            i=endpoints()
            print(intershow(i))
            g=supgen(f,i)
            print(g)
            #
            #   example 2
            #
            a=readgray('gear.tif')
            b=supgen(a,endpoints())
            show(a)
            show(dilate(b))
    """

    A,Bc = interval
    return intersec(erode(f,A),
                   erode(neg(f),Bc))


def bshow(f1, f2=None, f3=None, factor=17):
    """
    y = bshow(f1, f2=None, f3=None, factor=17)

    Generate a graphical representation of overlaid binary images.
    Does **not** actually display the image anywhere!

    Generate an expanded binary image as a graphical representation
    of up to three binary input images. The 1-pixels of the first
    image are represented by square contours, the pixels of the
    optional second image are represented by circles and for the
    third image they are represented by shaded squares. This
    function is useful to create graphical illustration of small
    images.

    Parameters
    ----------
    f1 :     Binary image.
    f2 :     Binary image. Default: None.
    f3 :     Binary image. Default: None.
    factor : Double Default: 17. Expansion factor for the output
                  image. Use odd values above 9.

    Returns
    -------
    y : Binary image.
    """
    import numpy
    from numpy import newaxis, zeros, resize, transpose, floor, arange, array

    if f1.shape == (): f1 = array([f1])
    if len(f1.shape) == 1: f1 = f1[newaxis,:]
    if f2 is not None and f1.shape != f2.shape or \
        f3 is not None and f1.shape != f3.shape or \
        f2 is not None and f3 is not None and f2.shape != f3.shape:
        raise ValueError('pymorph.bshow: arguments must have the same shape')
    s = factor
    if factor < 9: s = 9
    h,w = f1.shape
    y = zeros((s*h, s*w),numpy.int32)
    xc = resize(range(s), (s,s))
    yc = transpose(xc)
    r  = int(floor((s-8)/2. + 0.5))
    circle = (xc - s//2)**2 + (yc - s//2)**2 <= r**2
    r = arange(s) % 2
    fillrect = resize(array([r, 1-r]), (s,s))
    fillrect[ 0 , : ] = 0
    fillrect[s-1, : ] = 0
    fillrect[ : , 0 ] = 0
    fillrect[ : ,s-1] = 0
    for i in range(h):
        for j in range(w):
            m, n = s*i, s*j
            if f1 and f1[i,j]:
                y[m     ,n:n+s] = 1
                y[m+s-1 ,n:n+s] = 1
                y[m:m+s ,n    ] = 1
                y[m:m+s ,n+s-1] = 1
            if f2 and f2[i,j]:
                y[m:m+s, n:n+s] += circle
            if f3 and f3[i,j]:
                y[m:m+s, n:n+s] += fillrect
    return (y > 0)


def thin(f, Iab=None, n=-1, theta=45, direction="clockwise"):
    """
    y = thin(f, Iab={Homothin}, n={infinite}, theta=45, direction="clockwise")

    Image transformation by thinning.

    `thin` creates the binary image `y` by performing a thinning of the binary
    image `f`. The number of iterations of the thinning is n and each iteration
    is performed by subtracting the points that are detect in f by hit-miss
    operators characterized by rotations of theta of the interval `Iab`. When
    `n` is infinite and the interval is homothin (default conditions), thin
    gives the skeleton by thinning.

    Parameters
    ----------
    f :         Binary image.
    Iab :       Interval Default:(homothin).
    n :         Number of iterations. (default: -1, i.e. infinite)
    theta :     Double Default: 45. Degrees of rotation: 45, 90, or
                180.
    direction : One of ('clockwise', 'anti-clockwise'). default: clockwise.

    Returns
    -------
    y : Binary image.
    """
    """
    - Examples
      #
      f=readgray('scissors.tif')
      f1=thin(f)
      show(f,f1) # skeleton
      f2=thin(f1,endpoints(),15) # prunning 15 pixels
      show(f,f2) # prunned skeleton
    """
    from numpy import prod
    if Iab is None: Iab = homothin()
    direction = direction.lower()
    assert isbinary(f),'f must be binary image'
    if n == -1: n = prod(f.shape)
    y = f
    zero = intersec(f,0)
    for i in range(n):
        aux = zero
        for t in range(0,360,theta):
            sup = supgen(y, interot(Iab, t, direction))
            aux = union(aux, sup)
            y = subm(y, sup)
        if isequal(aux,zero): break
    return y


def union(f1, f2, *args):
    """
    y = union(f1, f2, f3=None, f4=None, f5=None, ...)

    Union of images.

    `union` creates the image `y` by taking the pixelwise maximum
    between the images given. When the images are binary images,
    y represents the union of them.

    Parameters
    ----------
    f1 : Gray-scale (uint8 or uint16) or binary image.
    f2 : Gray-scale (uint8 or uint16) or binary image. Or constant
    args : Gray-scale (uint8 or uint16) or binary images.

    Returns
    -------
    y : Image
    """
    """
        - Examples
            #
            #   example 1
            #
            f=to_uint8([255, 255,  0,  10,   0, 255, 250])
            print('f=',f)
            g=to_uint8([  0,  40, 80, 140, 250,  10,  30])
            print('g=',g)
            print(union(f, g))
            print(union(f, 255))
            #
            #   example 2
            #
            a = readgray('form-ok.tif')
            b = readgray('form-1.tif')
            c = union(a,b)
            show(a)
            show(b)
            show(c)
            #
            #   example 3
            #
            d = readgray('danaus.tif')
            e = (d < 80)
            f = union(d,gray(e))
            show(d)
            show(e)
            show(f)
            #
            #   example 4
            #
            g = readgray('tplayer1.tif')
            h = readgray('tplayer2.tif')
            i = readgray('tplayer3.tif')
            j = union(g,h,i)
            show(g)
            show(h)
            show(i)
            show(j)
    """
    from numpy import maximum

    y = maximum(f1,f2)
    for f in args:
        y = maximum(y,f)
    return y.astype(f1.dtype)


def maxleveltype(type='uint8'):
    """
    max = maxleveltype(type='uint8')

    Returns the maximum value supported by a datatype

    Parameters
    ----------
    type : { 'uint8' [default], 'uint16', 'int32'}

    Returns
    -------
    max : numeric value
        The maximum level value of `type`
    """
    if type == 'uint8': return 255
    if type == 'binary': return 1
    if type == 'uint16': return 65535
    if type == 'int32': return 2147483647
    assert False, 'pymorph.maxleveltype: does not support this data type:'+TYPE


def to_int32(f):
    """
    Convert an image to an int32 image.

    img = to_int32(f)

    `to_int32` clips the input image between the values -2147483648 and
    2147483647 and converts it to the signed 32-bit datatype.

    Parameters
    ----------
    f : Any image

    Returns
    -------
    img : The converted image
    """
    from numpy import int32, asanyarray
    return asanyarray(f).astype(int32)


def to_uint8(f):
    """
    img = to_uint8(f)

    Convert an image to an uint8 image.

    `to_uint8` clips the input image between the values 0 and 255 and
    converts it to the unsigned 8-bit datatype.

    Parameters
    ----------
    f : Any image

    Returns
    -------
    img : Gray-scale uint8 image. The converted image

    Examples
    --------
    ::

        print(to_uint8([-3, 0, 8, 600]))

    prints out

    ::

        [  0   0   8 255]
    """
    from numpy import array, clip, uint8

    img = array(clip(f,0,255),uint8)
    return img


def to_uint16(f):
    """
    img = to_uint16(f)

    Convert an image to a uint16 image.

    `to_uint16` clips the input image between the values 0 and 65535 and
    converts it to the unsigned 16-bit datatype.

    Parameters
    ----------
    f : Any image

    Returns
    -------
    img : The converted image
    """
    from numpy import array, clip

    img = array(clip(f,0,65535)).astype('H')
    return img


def add4dilate(f, c):
    """
    a = add4dilate(f, c)

    Addition for dilation. Assumes that the minimum value of dtype(f) is
    to represent -inf (where -inf + c == -inf, for all c)

    Parameters
    ----------
    f : Gray-scale or binary image.
    c : Gray-scale, binary image, or constant.

    Returns
    -------
    a : f + c (but with correct implementation of -inf)
    """
    from numpy import asarray, minimum, maximum, float64

    if not c:
        return f
    y = asarray(f,float64) + c
    k1,k2 = limits(f)
    y = ((f==k1) * k1) + ((f!=k1) * y)
    y = maximum(minimum(y,k2),k1)
    return y.astype(f.dtype)


def mat2set(A):
    """
    C,V = mat2set(A)

    Converts image representation from matrix to set

    Return tuple with array of pixel coordinates and array of
    corresponding pixel values. The input image is in the matrix
    format, like the structuring element, where the origin (0,0) is
    at the center of the matrix.

    Parameters
    ----------
    A : ndarray
        Image in matrix format, where the origin (0,0) is at the
        center of the matrix.

    Returns
    -------
    C : array of pixel coordinates
    V : array of pixel values corresponding to the coordinates of C

    See also
    --------
    set2mat : reverse function
    """
    from numpy import take, ravel, nonzero, transpose, newaxis

    if len(A.shape) == 1: A = A[newaxis,:]
    offsets = nonzero(ravel(A) - limits(A)[0])[0]
    if len(offsets) == 0: return ([],[])
    h,w = A.shape
    x = [0,1]
    x[0] = offsets//w - (h-1)//2
    x[1] = offsets%w - (w-1)//2
    x = transpose(x)
    return x,take(ravel(A),offsets)


def set2mat(A):
    """
    M = set2mat(A)

    Converts image representation from set to matrix

    Return an image in the matrix format built from a tuple of an
    array of pixel coordinates and a corresponding array of pixel
    values

    Parameters
    ----------
    A : tuple (ndarray, ndarray) or tuple (ndarray,)
        Tuple with array of pixel coordinates and optional array of
        corresponding pixel values

    Returns
    -------
    M : Image in matrix format, origin (0,0) at the matrix center


    Examples
    --------

    ::

        coords = to_int32([ [0,0] , [-1,0] , [1,1]])
        print(set2mat( (coords,) ))

    prints out

    ::

        [0,1,0]
        [0,1,0]
        [0,0,1]
    """
    from numpy import put, ones, ravel, shape, newaxis, array, asarray, max, int32
    import numpy as np

    if len(A) == 2:
        x, v = A
        v = asarray(v)
    elif len(A) == 1:
        x = A[0]
        v = np.ones((len(x),), np.uint8)
    else:
        raise TypeError('pymorph.set2mat: argument must be a tuple of length 1 or 2')
    if len(x) == 0:  return array([0]).astype(v.dtype)
    if len(x.shape) == 1: x = x[newaxis,:]
    dh,dw = abs(x).max(0)
    h,w = (2*dh)+1, (2*dw)+1
    M=ones((h,w),int32) * limits(v)[0]
    offset = x[:,0] * w + x[:,1] + (dh*w + dw)
    put(M,offset,v)
    return M.astype(v.dtype)


def pad4n(f, Bc, value, scale=1):
    """
    y = pad4n(f, Bc, value, scale=1)

    pads f with value so that Bc can be applied scaled by scale.

    Parameters
    ----------
    f :     Image
    Bc :    Structuring Element (connectivity).
    value : dtype
        value to pad borders with
    scale : (default=1).

    Returns
    -------
    y : The converted image
    """
    from numpy import ones, array

    if type(Bc) is not array:
      Bc = seshow(Bc)
    Bh, Bw = Bc.shape
    assert Bh%2 and Bw%2, 'structuring element must be odd sized'
    ch, cw = int(scale * Bh/2), int(scale * Bw/2)  # NumPy 1.x truncated float slice indices
    g = value * ones( f.shape + scale * (array(Bc.shape) - 1))
    g[ ch: -ch, cw: -cw] = f
    return g.astype(f.dtype)
