FROM milcom/centos7-systemd
# Copy repo inserted by Vagrant into our image, so we can install salt-minion.
COPY saltstack.repo /etc/yum.repos.d/
# Netstat is used by testinfra
RUN yum install -y epel-release initscripts salt-minion sudo net-tools; yum clean all
COPY minion /etc/salt/

ENTRYPOINT ["/usr/sbin/init"]
