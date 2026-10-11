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
docker run --rm -v /tmp/hidos-2016:/old -v "$PWD":/repo hidos-py27-baseline \
    python /repo/tools/py2-baseline/run.py /old/hidos-django/hidos /repo/hidos-django/hidos

# ported code, in a Python 3 environment with requirements/base.txt installed
python tools/py2-baseline/run.py hidos-django/hidos hidos-django/hidos
```

All six apps give identical numbers, except Cell M1 (18.70 in 2016, 18.43
now). Cell M1 reads images through `skimage.io` and Pillow, and Pillow 3.3
decoded the example JPEG differently from today's libjpeg-turbo based
decoders. Run on the same decoded pixels, the 2016 code also gives
18.4340112555.

To match the 2016 numbers, the port needed a few compatibility shims for
library changes since then. They are listed in `cell/skimage_compat.py`.
