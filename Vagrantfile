# coding: utf-8
# -*- mode: ruby -*-
# vi: set ft=ruby :
BOX_IMAGE = "debian/stretch64"
Vagrant.configure("2") do |config|

    config.vm.box = BOX_IMAGE
    config.vm.hostname = "web-AI-5"

    # Der Webserver ist unter http://localhost:8000 erreichbar
    config.vm.network "forwarded_port", guest: 80, host: 8000

    #Diese Option würde erlauben den Server an ein virtuelles
    #Netzwerk anzuschliessen.
    #config.vm.network "private_network", type: "dhcp"

    #Begin des Installationsscripts
    config.vm.provision "shell", inline: <<-SHELL
    DEBIAN_FRONTEND=noninteractive
    apt-get update

    #zu installierende Pakete
    apt-get install -y apache2 php7.0 php7.0-mysql php7.0-xml mariadb-server avahi-daemon libnss-mdns

    #aktiviert das MySQL Modul für den Apache Webserver
    phpenmod mysqli

    #So würde der Code aussehen um SQL Scripts in die DB zu importieren.
    #mysql < /vagrant/sql/remove_db.sql
    #mysql < /vagrant/sql/create_db.sql
    #mysql < /vagrant/sql/add_data.sql

    #löschen und verlinken der HTML root damit man diese nicht manuel kopieren muss.
    if ! [ -L /var/www/html ]; then
        rm -rf /var/www/html
        ln -s /vagrant/html /var/www/html
    fi
    SHELL

end
