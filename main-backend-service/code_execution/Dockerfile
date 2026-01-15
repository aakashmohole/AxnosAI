FROM python:3.12-slim

# install common data libs
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    scipy \
    scikit-learn \
    matplotlib \
    seaborn

WORKDIR /app

CMD ["python"]
