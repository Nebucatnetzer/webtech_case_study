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
    config.vm.network "forwarded_port", guest: 80, host: 8000

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
        libnss-mdns libapache2-mod-wsgi-py3 python3-mysqldb 


    #So würde der Code aussehen um SQL Scripts in die DB zu importieren.
    #mysql < /vagrant/sql/remove_db.sql
    #mysql < /vagrant/sql/create_db.sql
    #mysql < /vagrant/sql/add_data.sql

    #löschen und verlinken der HTML root damit man diese nicht manuel kopieren muss.
    if ! [ -L /var/www/html ]; then
        rm -rf /var/www/html
        ln -s /vagrant/html /var/www/html
    fi

    #Copy the apache configuration for django to the correct place
    cp /vagrant/apache/000-default.conf /etc/apache2/sites-available/
    #restart the webserver
    systemctl restart apache2.service
    SHELL

end
