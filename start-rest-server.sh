#!/bin/bash
set -e

mkdir -p run
cd run

sudo apt-get update
sudo apt-get install -y python3 python3-pip git
git clone https://github.com/sricke/lab6-rest-vs-grpc.git
cd lab6-rest-vs-grpc
sudo pip3 install -r requirements.txt

nohup python3 rest-server.py &