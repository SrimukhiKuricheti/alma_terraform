terraform {
 required_version = ">= 0.13"
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "0.7.1"
    }
  }
}

# instance the provider
provider "libvirt" {
  uri = "qemu:///system"
}

resource "libvirt_pool" "almalinux_new" {
  name = "almalinux_new"
  type = "dir"
  path = "/tmp/terraform-provider-libvirt-pool-alma_new"
	
}

resource "libvirt_volume" "almalinux-qcow2" {
  name   = "almalinux-qcow2"
  pool   = libvirt_pool.almalinux_new.name
  source= "https://repo.almalinux.org/almalinux/8/cloud/x86_64/images/AlmaLinux-8-GenericCloud-8.8-20230524.x86_64.qcow2"
  format = "qcow2"
}

data "template_file" "user_data" {
  template = file("${path.module}/cloud_init.cfg")
}

data "template_file" "network_config" {
  template = file("${path.module}/network_config.cfg")
}

resource "libvirt_cloudinit_disk" "commoninit" {
  name           = "commoninit.iso"
  user_data      = data.template_file.user_data.rendered
  network_config = data.template_file.network_config.rendered
  pool           = libvirt_pool.almalinux_new.name
}

# Create the machine
resource "libvirt_domain" "domain-almalinux" {
  name   = "almalinux-terraform"
  memory = "3062"
  vcpu   = 6  

  cloudinit = libvirt_cloudinit_disk.commoninit.id

  network_interface {
    network_name = "default"
    wait_for_lease = true
  }

  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  console {
    type        = "pty"
    target_type = "virtio"
    target_port = "1"
  }

  disk {
    volume_id = libvirt_volume.almalinux-qcow2.id
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
    autoport    = true
  }

  provisioner "file" {
    source      = "ldap_setup.sh"
    destination = "ldap_setup.sh"
  }

  provisioner "file" {
    source = "user1.ldif"
    destination = "user1.ldif"
  }

  provisioner "file" {
    source = "group1.ldif"
    destination = "group1.ldif"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x ldap_setup.sh",  # Make the script executable
      "./ldap_setup.sh",           # Execute your script
    ]
  }

  connection {
    host = "${libvirt_domain.domain-almalinux.network_interface.0.addresses.0}"
    type = "ssh"
    user = "almalinux"
    password = "P@$$W0RD"
  }
  
  provisioner "local-exec" {
    command = "iptables -I PREROUTING -t nat -i ens192 -p tcp -m tcp --dport 49389 -j DNAT --to-destination ${libvirt_domain.domain-almalinux.network_interface.0.addresses.0}:389"
  }
}

resource "null_resource" "clean_iptables" {
  triggers = {
  host = "${libvirt_domain.domain-almalinux.network_interface.0.addresses.0}:389"
  }
  
  provisioner "local-exec" {
    when = destroy
    command = <<CMD
    iptables -D PREROUTING -t nat -i ens192 -p tcp -m tcp --dport 49389 -j DNAT --to-destination "${self.triggers.host}"
    CMD
  }
}

output "ip" {
  value = "${libvirt_domain.domain-almalinux.network_interface.0.addresses.0}"
}

# IPs: use wait_for_lease true or after creation use terraform refresh and terraform show for the ips of domain
