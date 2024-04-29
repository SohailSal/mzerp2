Installation steps:

git clone https://github.com/sohailsal/mzerp2
cd mzerp2
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
(enter a username, then email and password...remember them)
python manage.py loaddata base/sample
python manage.py loaddata ledger/sample
python manage.py runserver
goto localhost:8000 and login with the above username and password