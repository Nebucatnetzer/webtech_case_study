# web_AI-5

This repository contains the code to the case study Ivan and Andreas had to
make during the 5th semester.
The repository exists mostly as a place to work together and for educational
purposes in case someone needs inspiration for this own school projects.

Dieses Repository enthält den Code der Webtechnologie Case Study von Ivan und
Andreas. Das Repository existiert hauptsächlich für die Zusammenarbeit sowie als
Inspiration falls jemand ähnlich Schulprojekte hat.

### Installation und Guidelines

##### Installation

To get started with this repository make sure that you have Virtualbox
5.1.30 and Vagrant 2.0.0 installed. Vagrant 2.0.0 currently doesn't
support Virtualbox 5.2.

After you have installed Vagrant and Virtualbox run this command in a
terminal to make sure that you have installed the Virtualbox plugin
for Vagrant.

``` bash
vagrant plugin install vagrant-vbguest
```

To start the virtual machine then run this command from the root of
the repository (where the file "Vagrantfile" is stored).

``` bash
vagrant up
```

Vagrant will then provision a virtual machine according to the
specifications in the "Vagrantfile" file. After it's finished you
should be able to access the web page under http://localhost:8080

To access the admin panel visit http://localhost:8080/admin the
default login is admin and the corresponding password is
"password". By default the application contains no data, you can enter
whatever you need.

### Support

We don't provide any support for the content in this repository.

### License

The project is licensed under the GPLv3 license.
