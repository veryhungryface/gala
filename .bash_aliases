alias reinstall='sudo gala-node stop && sudo gala-node remove && sudo rm -rf DownloadLinuxNode && sudo wget -O gala.tar.gz --trust-server-names https://links.gala.com/DownloadLinuxNode && sudo tar xzvf gala.tar.gz && yes|sudo ./gala-node/install.sh && sudo gala-node start'
