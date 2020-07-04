cmd /C env\scripts\activate

set FLASK_APP=src\api.py
set FLASK_ENV=development
flask run