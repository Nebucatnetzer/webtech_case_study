#initialize the db
mysql < /vagrant/sql/04_remove_database.sql
mysql < /vagrant/sql/01_create_database.sql

#remove old migrations
rm /vagrant/django/didgeridoo/webshop/migrations/*.py

#create and insert the new migrations
python3 /vagrant/django/didgeridoo/manage.py makemigrations webshop
python3 /vagrant/django/didgeridoo/manage.py migrate

#insert some default data into the database
mysql < /vagrant/sql/02_insert_data.sql

#create an admin user
echo "from django.contrib.auth.models import User; \
      User.objects.filter(email='admin@example.com').delete(); \
      User.objects.create_superuser('admin', 'admin@example.com', 'password')" |
      python3 /vagrant/django/didgeridoo/manage.py shell

python3 /vagrant/django/didgeridoo/manage.py loaddata webshop
