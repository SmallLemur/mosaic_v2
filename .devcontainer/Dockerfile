FROM registry.gitlab.com/project_k1/processing/dem-generator:master
#FROM jupyter/datascience-notebook:latest
# install requirements
ADD ./.devcontainer/requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt