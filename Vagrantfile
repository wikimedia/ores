# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "debian/jessie64"
  config.vm.box_url = 'https://atlas.hashicorp.com/ARTACK/boxes/debian-jessie'
  
  config.vm.provision "shell", path: 'provision.bash'

  config.vm.network "forwarded_port", guest: 8080, host: 8080
end
