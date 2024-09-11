REMOTE COMPUTER

1) Install Ubuntu

2) go to https://github.com/krakenrf/krakensdr_docs/wiki/09.-VirtualBox,-Docker-Images-and-Install-Scripts#virtualbox

3) open terminal & run comamnds

  INSTALL KrakenSDR software
  
  $ wget https://raw.githubusercontent.com/krakenrf/krakensdr_docs/main/install_scripts/krakensdr_x86_install_doa.sh
  
  $ sudo chmod +x krakensdr_x86_install_doa.sh
  
  $ ./krakensdr_x86_install_doa.sh

  INSTALL SSH, NETWORK UTIL
  
  $ apt install openssh-server 
  
  $ sudo apt install net-tools

4) cd /home/krakensdr/krakensdr_doa

5) START SEREVR 

  $ ./kraken_doa_start.sh
  
  STOP SEREVR 
  
  $ ./kraken_doa_stop.sh

==================================================================

$ ./kraken_doa_start.sh 

Shut down DAQ chain ..
Config file check bypassed [ WARNING ]
kernel.sched_rt_runtime_us = -1
Desig FIR filter with the following parameters: 
Decimation ratio: 1
Bandwidth: 1.00
Tap size: 1
Window function: hann
FIR filter ready
Transfer funcfion is exported to :  _logs/Decimator_filter_transfer.html
Coefficients are exported to:  _data_control/fir_coeffs.txt
Starting DAQ Subsystem
Output data interface: Shared memory

               
Have a coffee watch radar

Remote Control is DISABLED
To enable Remote Control please install miniserve and jq.
Then change 'en_remote_control' setting in _share/settings.json file to 'true'.
Finally, apply settings by restarting the software.

Starting KrakenSDR Direction Finder
Web Interface Running at 0.0.0.0:8080
Data Out Server Running at 0.0.0.0:8081
TAK Server Installed

$ ifconfig

eno1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.10.1.93  netmask 255.255.255.0  broadcast 10.10.1.255

==================================================================

your IP KrekenSDR server 10.10.1.93:8080

6) open link in browser http://10.10.1.93:8080/
   
6.1) - Configuration open http://10.10.1.93:8080/config

  choose Center Frequency [MHz]: 100
  
  push the botton "Update Receiver Parameters"
  
6.3) - DoA Estimation open http://10.10.1.93:8080/doa

7) krakensdr_map.py
   
  ws_url_1 = "ws://10.10.1.93:8080/_push"
  
  ws_url_2 = "ws://10.10.1.93:8080/_push"
  
 change your IP

8) RUN krakensdr_map.py
