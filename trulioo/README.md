# Passfort Trulioo integration

#### Tools
 - Python 3.7
 - Flask
 - Pipenv
 - Pytest
 
# Instalation

Requirements: **Python 3.7**

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
$ docker build --tag=trulioo:1.1 -f Dockerfile .
```
# Run docker image
```sh
$ docker run -p 8001:8001 --name trulioo_integration trulioo:1.1
```
# End points
```sh
POST /ekyc-check
POST /health
```
Health check example
```sh
curl http://127.0.0.1:8001/health
"Trulioo Integration" ( 200 )
  ```
