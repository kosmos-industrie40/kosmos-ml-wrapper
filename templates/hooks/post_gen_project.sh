#!/bin/bash

if ! grep -Fxq "GET_STARTED.md" .gitignore
then
  echo "GET_STARTED.md" >> .gitignore
fi

cp ~/.cookiecutter_replay/templates.json ./.cookiecutter_generation_variables.json

mkdir -p deployment/k8s

mv deployment.yaml deployment/k8s/

if ! black --version &> /dev/null
then
  echo "You will have to reformat using black yourself, because black is not available globally"
else
  black src
  black tests
fi



