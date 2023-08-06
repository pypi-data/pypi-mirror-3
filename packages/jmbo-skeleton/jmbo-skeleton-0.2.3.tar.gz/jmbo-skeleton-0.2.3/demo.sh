#!/bin/sh

echo "The demo app checks out code from github and uses sqlite as backend. Installation is confined to this directory."
echo "Choose the Python version to use:"
choice=3
echo "1. 2.6"
echo "2. 2.7"
while [ $choice -eq 3 ]; do
    read choice
    read -p "Installing required libraries. You may be prompted for a password. [enter]" y
    if [ $choice -eq 1 ] ; then
	if [ -f ./ve/bin/python2.7 ];
	then
	    sudo rm -rf ./ve ./bin
	fi
        sudo apt-get install python-virtualenv python2.6-dev \
	libjpeg62-dev libjpeg62-dev zlib1g-dev build-essential git-core --no-upgrade
	echo "Setting up sandboxed Python environment with Python 2.6"
	virtualenv --python=python2.6 --no-site-packages ve
    else
	if [ -f ./ve/bin/python2.6 ];
	then
	    sudo rm -rf ./ve ./bin
	fi
	sudo apt-get install python-virtualenv python2.7-dev \
	libjpeg62-dev libjpeg62-dev zlib1g-dev build-essential git-core --no-upgrade
	echo "Setting up sandboxed Python environment with Python 2.7"
	virtualenv --python=python2.7 --no-site-packages ve
    fi
done
echo "Downloading distribute"
ve/bin/python bootstrap.py
echo "Choose the type of demo site:"
choice=3
echo "1. Basic (mobi for low-end handsets)"
echo "2. Web"
SITE_TYPE=basic
while [ $choice -eq 3 ]; do
    read choice
    if [ $choice -eq 1 ] ; then
        read -p "This part may take a while. If it fails with 'connection reset by peer' run ./install-app again. [enter]" y
        ./bin/buildout -nv -c dev_basic_site.cfg
    else
        read -p "This part may take a while. If it fails with 'connection reset by peer' run ./install-app again. [enter]" y
        ./bin/buildout -nv -c dev_web_site.cfg
        SITE_TYPE=web
    fi
done

# Remove stale database
if [ -f /tmp/skeleton.sql ];
then
    rm /tmp/skeleton.sql
fi

read -p "Create a superuser when prompted. Do not generate default content. [enter]" y
./bin/skeleton-dev-$SITE_TYPE-site syncdb
./bin/skeleton-dev-$SITE_TYPE-site migrate
./bin/skeleton-dev-$SITE_TYPE-site load_photosizes
rm -rf static
./bin/skeleton-dev-$SITE_TYPE-site collectstatic --noinput
echo "You may now start up the site with ./bin/skeleton-dev-$SITE_TYPE-site runserver 0.0.0.0:8000"
echo "Browse to http://localhost:8000/ for the public site."
echo "Browse to http://localhost:8000/admin for the admin interface."
