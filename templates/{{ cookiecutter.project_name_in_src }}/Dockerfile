# Build a virtualenv using the appropriate Debian release
# * Install python3-venv for the built-in Python3 venv module (not installed by default)
# * Install gcc libpython3-dev to compile C Python modules
# * Update pip to support bdist_wheel
ARG GIT_TOKEN
ARG GIT_USER
FROM debian:buster-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev git && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install wheel


# Build the virtualenv as a separate step: Only re-execute this step when requirements.txt changes
FROM build AS build-venv
ARG GIT_TOKEN
ARG GIT_USER
COPY . /app
RUN git config --global url."https://$GIT_USER:$GIT_TOKEN@gitlab.inovex.de".insteadOf https://gitlab.inovex.de
WORKDIR /app
RUN /venv/bin/pip install -r requirements.txt
RUN /venv/bin/python setup.py install

# Copy the virtualenv into a distroless image
FROM gcr.io/distroless/python3-debian10
USER nonroot:nonroot
ENV PYTHONUNBUFFERED=1
COPY --from=build-venv /venv /venv
COPY ./src /src
COPY __main__.py /__main__.py
ENTRYPOINT ["/venv/bin/python3", "__main__.py"]
