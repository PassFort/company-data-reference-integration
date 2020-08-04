# Passfort Loqate integration

#### Tools
 - Python 3.7
 - Flask
 - Pipenv
 - Pytest
 
# Installation

Requeriments: **Python 3.7**

```sh
#Prod
$ pipenv install

#Dev
$ pipenv install --dev
```
All the projects dependeces will be installed
**If you are not using `pipenv` just remove before the commands `pipenv run`**

# Running the project
```sh
$ pipenv run flask run
```
# Running the tests ( need install the dev dependences " --dev ")

```sh
$ pipenv run pytest

#Create converage report
$ pipenv run coverage run -m pytest

#Show coverage report
$ pipenv run coverage report
```
# Build docker image
```sh
$ docker build --tag=Loqate:0.1 -f docker/Dockerfile .
```
# Run docker image
```sh
$ docker run -p 8001:8001 --name loqate_integration Loqate:0.1
```
# End points
```sh
POST /health
```
