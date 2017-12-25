mysql < /vagrant/sql/04_remove_database.sql
mysql < /vagrant/sql/01_create_database.sql
rm /vagrant/django/didgeridoo/webshop/migrations/*.py
python3 /vagrant/django/didgeridoo/manage.py makemigrations webshop
python3 /vagrant/django/didgeridoo/manage.py migrate
mysql < /vagrant/sql/02_insert_data.sql
