# Test News site

## Requirements
Python3.7

## Install
```
git clone https://github.com/overmesgit/test_news_project

cd test_news_project

python3.7 -m venv env

source env/bin/activate

pip install -r requirements.txt
```
Set secret key and allow host for production use or 
use --settings=news_project.dev_settings for creating dev environment
```
./manage.py migrate --settings=news_project.dev_settings

./manage.py test --settings=news_project.dev_settings
```
## Download news
```
./manage.py fetch_news -k <API_KEY> --settings=news_project.dev_settings
```
Take fetch_news command help for more information

## Debug Run
```
./manage.py runserver --settings=news_project.dev_settings
```

## Production Run
Set secret key and allow host for production use
```
./manage.py runserver
```

## Structure
About django rest framework and throttling.

Main models

Unique key for news

## Todo
fix fetch data errors