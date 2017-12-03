# coding: utf-8
# -*- mode: ruby -*-
# vi: set ft=ruby :
BOX_IMAGE = "debian/stretch64"
Vagrant.configure("2") do |config|

    config.vm.box = BOX_IMAGE
    config.vm.hostname = "web-AI-5"
    config.vm.provider "virtualbox" do |v|
        v.memory = 1024
        v.cpus = 2
    end


    # Der Webserver ist unter http://localhost:8000 erreichbar
    config.vm.network "forwarded_port", guest: 8000, host: 8000
    config.vm.network "forwarded_port", guest: 80, host: 8080

    #Diese Option würde erlauben den Server an ein virtuelles
    #Netzwerk anzuschliessen.
    #config.vm.network "private_network", type: "dhcp"

    config.vm.synced_folder ".", "/vagrant", type: "virtualbox"

    #Begin des Installationsscripts
    config.vm.provision "shell", inline: <<-SHELL
    DEBIAN_FRONTEND=noninteractive
    apt-get update

    #zu installierende Pakete
    apt-get install -y apache2 python3-django mariadb-server avahi-daemon \
        libnss-mdns libapache2-mod-wsgi-py3 python3-mysqldb python3-pip
    pip3 install django-extensions


    #initialize the db
    mysql < /vagrant/sql/04_remove_database.sql
    mysql < /vagrant/sql/01_create_database.sql

    #löschen und verlinken der HTML root damit man diese nicht manuel kopieren muss.
    if ! [ -L /var/www/html ]; then
        rm -rf /var/www/html
        ln -s /vagrant/html /var/www/html
    fi

    #Copy the apache configuration for django to the correct place
    cp /vagrant/apache/000-default.conf /etc/apache2/sites-available/
    #restart the webserver
    systemctl restart apache2.service
    rm /vagrant/django/didgeridoo/webshop/migrations/*.py
    python3 /vagrant/django/didgeridoo/manage.py makemigrations webshop
    python3 /vagrant/django/didgeridoo/manage.py migrate
    mysql < /vagrant/sql/02_insert_data.sql
    echo "from django.contrib.auth.models import User; \
        User.objects.filter(email='admin@example.com').delete(); \
        User.objects.create_superuser('admin', 'admin@example.com', 'password')" |
        python3 /vagrant/django/didgeridoo/manage.py shell
    SHELL

end
