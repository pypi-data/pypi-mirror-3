#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handle the templates to configure user-data.
"""
import os
import re
from jinja2 import Environment
from jinja2 import FileSystemLoader

from shaker import __version__

CLOUD_INIT_PREFIX = 'cloud-init'
USER_SCRIPT_PREFIX = 'user-script'


class UserData(object):
    def __init__(self, config):
        cfg = {'version': __version__}
        cfg.update(config)
        self.cloud_init_name = "%s.%s" % (CLOUD_INIT_PREFIX, __version__)
        self.user_script_name = "%s.%s" % (USER_SCRIPT_PREFIX, __version__)
        self.template_dir = self.get_template_dir(cfg['config_dir'])
        env = Environment(loader=FileSystemLoader(self.template_dir))
        self.user_script = re.sub(
            '\n\n+',
            '\n\n',
            env.get_template(self.user_script_name).render(cfg))
        self.cloud_init = re.sub(
            '\n\n+',
            '\n\n',
            env.get_template(self.cloud_init_name).render(cfg))

    def get_template_dir(self, config_dir):
        """Return the template directory name, creating the
        directory if absent (and populating with boilerplate).
        """
        template_dir = os.path.join(config_dir, 'templates')
        if not os.path.isdir(template_dir):
            os.makedirs(template_dir)
        for filename, template in [(self.cloud_init_name, CLOUD_INIT),
                                   (self.user_script_name, USER_SCRIPT),]:
            path = os.path.join(template_dir, filename)
            if not os.path.isfile(path):
                with open(path, 'w') as f:
                    f.write(template)
        return template_dir


CLOUD_INIT = """#cloud-config
# Shaker version: {{ version }}
{% if salt_master %}
{% if not ec2_distro in ['lucid', 'maverick', 'natty'] %}
apt_sources:
  - source: "ppa:saltstack/salt"

apt_upgrade: true
{% endif %}
{% endif %}

{% if ssh_import %}
ssh_import_id: [{{ ssh_import }}]
{% endif %}

{% if hostname %}
hostname: {{ hostname }}
{% if domain %}
fqdn: {{ hostname }}.{{ domain }}
{% endif %}
{% endif %}
"""

USER_SCRIPT = """#!/bin/sh
# Shaker version: {{ version }}
{% if timezone %}
# set timezone
echo "{{ timezone }}" | tee /etc/timezone
dpkg-reconfigure --frontend noninteractive tzdata
restart cron
{% endif %}

{% if domain and hostname %}
sed -i "s/127.0.0.1 ubuntu/127.0.0.1 localhost {{ hostname }}.{{ domain }} {{ hostname }}/" /etc/hosts
# temp work-around for cloudinit bug: https://bugs.launchpad.net/cloud-init/
echo "127.0.0.1 localhost {{ hostname }}.{{ domain }} {{ hostname }}" >> /etc/hosts
{% elif hostname %}
  hostname: {{ hostname }}
{% endif %}

{% if ssh_port and ssh_port != '22' %}
# change ssh port 22 to non-standard port and restart sshd
sed -i "s/^Port 22$/Port {{ ssh_port }}/" /etc/ssh/sshd_config
/etc/init.d/ssh restart
{% endif %}

{% if sudouser %}
# create new user with sudo privileges
useradd -m -s /bin/bash {{ sudouser }}
{% if ssh_import %}cp -rp /home/ubuntu/.ssh /home/{{ sudouser }}/.ssh
chown -R {{ sudouser }}:{{ sudouser }} /home/{{ sudouser }}/.ssh
{% endif %}
echo "{{ sudouser }} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
{% endif %}

{% if size and root_device %}
# resize the filesystem to use specified space
resize2fs {{ root_device }}
{% endif %}

{% if salt_master %}
# Install salt-minion and run as daemon

{% if ec2_distro in ['lucid', 'maverick'] %}
aptitude -y install python-software-properties && add-apt-repository ppa:chris-lea/libpgm && add-apt-repository ppa:chris-lea/zeromq && add-apt-repository ppa:saltstack/salt && aptitude update
{% endif %}

apt-get -y install salt

MINION_CONFIG=/etc/salt/minion
cp $MINION_CONFIG.template $MINION_CONFIG
sed -i "s/#master: salt/master: {{ salt_master }}/" $MINION_CONFIG
# hack to install upstart config -- until it's added to the salt distro
SALT_MINION_UPSTART="https://raw.github.com/gist/1617054/1c2f1200f86252eb690dc599d0dec11e2df16e8c/salt-minion.conf"
curl $SALT_MINION_UPSTART -o /etc/init/salt-minion.conf
{% if salt_id %}
sed -i "s/#id:/id: {{ salt_id }}/" $MINION_CONFIG
{% endif %}
# start salt-minion daemon
salt-minion -d
{% endif %}
"""