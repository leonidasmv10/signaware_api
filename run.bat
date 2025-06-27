@echo off

echo Activating virtual environment...
call .\env\Scripts\activate

echo Invoke...
py manage.py runserver