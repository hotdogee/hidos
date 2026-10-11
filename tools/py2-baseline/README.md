# Python 2.7 baseline of the analysis algorithms

The algorithms in `hidos-django/hidos/<app>/bin/` were ported from Python 2.7
to Python 3 in 2026. This directory rebuilds the 2016 environment, so the
results of the original code can be compared with the port.
`cell/test_analysis.py` checks the port against numbers produced this way.

```sh
docker build -t hidos-py27-baseline tools/py2-baseline

# the last commit before the Python 3 port
mkdir -p /tmp/hidos-2016 && git archive 919104b hidos-django/hidos | tar -x -C /tmp/hidos-2016

# original code on the example images (taken from the current checkout)
# and on the colour photos of the tests
docker run --rm -v /tmp/hidos-2016:/old -v "$PWD":/repo hidos-py27-baseline \
    python /repo/tools/py2-baseline/run.py /old/hidos-django/hidos /repo/hidos-django/hidos \
    /repo/hidos-django/hidos/cell/testdata/IMG_0126_tungsten_800.png /repo/hidos-django/hidos/cell/testdata/IMG_0159_640.png

# ported code, in a Python 3 environment with requirements/base.txt installed
python tools/py2-baseline/run.py hidos-django/hidos hidos-django/hidos hidos-django/hidos/cell/testdata/*.png
```

On the example images and on the two colour photos in `cell/testdata`, the
port gives the 2016 numbers for all six apps, with two exceptions:

* Cell M1 on its example (18.70 in 2016, 18.43 now). Cell M1 reads images
  through `skimage.io` and Pillow, and Pillow 3.3 decoded the example JPEG
  differently from today's libjpeg-turbo based decoders. Run on the same
  decoded pixels, the 2016 code also gives 18.4340112555.
* Cell M1 on `IMG_0159_640.png` (24.955312 in 2016, 24.955455 now). Cell M1
  and Cell M3 resize with scikit-image 0.12, which estimated the scaling
  matrix with an SVD. Its last bits depend on the LAPACK build and the CPU,
  and the algorithms truncate the resized values, so on some images the 2016
  code itself gives different numbers on different CPUs (add
  `-e OPENBLAS_CORETYPE=Haswell` or `Sandybridge` to the `docker run`
  above). The port uses the exact matrix instead. For these two apps it
  matches 2016 only where the 2016 result did not depend on the CPU. Given
  the matrices that the 2016 code computed, it reproduces the 2016 numbers.

The example images are grey (R = G = B). For colour photos the 2016 code
used OpenCV 3's conversion to grey, which rounds differently from OpenCV 4.

The ported code gives the same numbers on Linux and Windows, with and
without AVX-512. To check this on Linux, run `pytest -m analysis` in a
`python:3.x-slim` container with `requirements/test.txt` installed: once as
it is, and once with
`-e NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL AVX512_SPR" -e OPENBLAS_CORETYPE=Haswell`.

To match the 2016 numbers, the port needed a few compatibility shims for
library changes since then, and it avoids library functions whose last bits
depend on the CPU (`np.hypot`, the `np.exp` in scipy's Gaussian kernel, the
SVD). They are listed in `cell/skimage_compat.py`.
