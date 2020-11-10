#!/bin/bash
# This script is used to provision an ol-coversX node _before_ docker gets on it.

# Which Ubuntu release are we running on?  Do not fail if /etc/os-release does not exist.
cat /etc/os-release | grep VERSION= || true  # VERSION="20.04.1 LTS (Focal Fossa)"
SERVICE=${SERVICE:-"covers"}

# CAUTION: To git clone olsystem, environment variables must be set...
# Set $GITHUB_USERNAME or $USER will be used.
# Set $GITHUB_TOKEN or this script will halt.
if [[ -z ${GITHUB_TOKEN} ]]; then
    echo "FATAL: Can not git clone olsystem" ;
    exit 1 ;
fi

# apt list --installed
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
docker --version        # 19.03.8
docker-compose version  #  1.25.0
sudo systemctl start docker
sudo systemctl enable docker

sudo groupadd --system openlibrary
sudo useradd --no-log-init --system --gid openlibrary --create-home openlibrary

cd /opt
ls -Fla  # nothing

sudo git clone https://${GITHUB_USERNAME:-$USER}:${GITHUB_TOKEN}@github.com/internetarchive/olsystem

OL_DOMAIN=${OL_DOMAIN:-internetarchive}
sudo git clone https://github.com/$OL_DOMAIN/openlibrary
ls -Fla  # containerd, olsystem, openlibrary owned by openlibrary

cd /opt/openlibrary
OL_BRANCH=${OL_BRANCH:-master}
sudo git checkout $OL_BRANCH
sudo make git
cd /opt/openlibrary/vendor/infogami && sudo git pull origin master

echo "Starting $SERVICE"
cd /opt/openlibrary
sudo docker-compose build --pull $SERVICE

sudo docker-compose down
sudo docker-compose up -d --no-deps memcached  # TODO: Does covers use memcached?
sudo docker-compose \
    -f docker-compose.yml \
    -f docker-compose.infogami-local.yml \
    -f docker-compose.production.yml \
    up -d --no-deps $SERVICE
sudo docker-compose logs -f --tail=100 $SERVICE
