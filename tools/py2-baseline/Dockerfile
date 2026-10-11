# The 2016 analysis environment: Python 2.7 with the library versions of
# hidos-django/hidos/requirements/base.txt at the time (numpy 1.11.1,
# scipy 0.17.1, scikit-image 0.12.3, mahotas 1.4.3, pymorph 0.96,
# Pillow 3.3.0). OpenCV was built from source in 2016 (install_opencv.sh);
# 3.4.0.14 is the oldest opencv-python wheel still on PyPI.
FROM python:2.7.18-buster
ENV MPLBACKEND=Agg PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip install --no-cache-dir numpy==1.11.1 && \
    pip install --no-cache-dir scipy==0.17.1 Pillow==3.3.0 six==1.10.0 networkx==1.11 toolz==0.8.0 dask==0.11.0 matplotlib==1.5.3 && \
    pip install --no-cache-dir --no-deps scikit-image==0.12.3 && \
    pip install --no-cache-dir mahotas==1.4.3 pymorph==0.96 && \
    pip install --no-cache-dir --no-deps opencv-python==3.4.0.14
