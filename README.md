# Test News site

Test site for presentation purpose

## Requirements
Python3.6+

Originally developed with python3.7, but also was tested with python3.6

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
### End points
Html version of site:

http://127.0.0.1:8000/

Json version of site, paginated by 'page' parameter

http://127.0.0.1:8000/api/v1/news/

## Production Run
Set secret key and allow host in settings for production use
```
./manage.py runserver
```

## Structure
####
Currently solution consist from one application - news

Main parts:

- models with NewsModel and NewsSourceModel
- scrapers with base structure and implementation for apinews.org
- views for http views
- views_api for api views

#### About django rest framework and throttling
Creating REST API with django, django-rest-framework is the most popular and convenient way.
Because in test description was mentioned not to use unnecessary frameworks, 
I decided to make it from scratch. So I could not use django-rest-framework Throttling class and 
created my own middleware.
