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
    pip3 install django-extensions Pillow pyaml django-bootstrap3


    #Copy the apache configuration for django to the correct place
    cp /vagrant/apache/000-default.conf /etc/apache2/sites-available/

    mkdir -p /srv/media/images
    chmod -R 777 /srv/media

    #restart the webserver
    systemctl restart apache2.service

    /vagrant/ansible/roles/web_AI-5/tasks/setup_script.sh

    #insert the currency update cronjob
    echo "wget -O /dev/null http://localhost:8080" > /etc/cron.hourly/currency_update
    chmod +x /etc/cron.hourly/currency_update
    SHELL

end
