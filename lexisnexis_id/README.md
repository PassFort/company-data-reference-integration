# Passfort LexisNexis integration

#### Tools
 - Python 3.7
 - Flask
 - Pipenv
 - Pytest
 
# Instalation

Requeriments: **Python 3.7**

```sh
#Prod
$ pipenv install

#Dev
$ pipenv install --dev
```
All the projects dependeces will be installed
**If you are not using `pipenv` just remove before the commands `pipenv run`**

# Configuration
Config the env vars `HTTP_PROXY` and `HTTPS_PROXY` with a valid proxy for tunneling the requests, if required.

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
$ docker build --tag=LexisNexis:0.1 -f docker/Dockerfile .
```
# Run docker image
```sh
$ docker run -p 8001:8001 --name lexisnexis_integration LexisNexis:0.1
```
# End points
```sh
POST /ekyc-check
POST /health
```
Health check example
```sh
curl --request POST \
  --url http://127.0.0.1:8001/health \
  --header ': ' \
  --header 'Content-Type: application/json' \
  --data '{"credentials": {"username":"lexisnexis_user","password":"lexisnexis_pass", "url":"https://..."}}'

"LexisNexis Integration" ( 200 )
  ```