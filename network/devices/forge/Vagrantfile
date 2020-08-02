Vagrant.configure('2') do |config|

  # Box Setup
  config.vm.box = 'debian/contrib-testing64'
  config.vm.provision 'shell', path: '.vagrant/bootstrap'

  # Shared Dirs
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/home/vagrant/.sync"

  # Providers
  config.vm.provider "virtualbox"

  # Virtualbox
  config.vm.provider 'virtualbox' do |vb|
    vb.gui = false
    vb.memory = '4096'
  end

  # Post-Deploy Message
  config.vm.post_up_message = <<-EOF
    Dev box deployed!
  EOF

end
