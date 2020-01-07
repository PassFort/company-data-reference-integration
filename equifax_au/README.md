# Passfort Equifax integration

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
$ docker build --tag=Equifax:0.1 -f docker/Dockerfile .
```
# Run docker image
```sh
$ docker run -p 8001:8001 --name equifax_integration Equifax:0.1
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
  --data '{"credentials": {"username":"equifax_user","password":"equifax_pass","url": "https://apiconnect.equifax.com.au/"}}'

"Equifax Integration" ( 200 )
  ```
