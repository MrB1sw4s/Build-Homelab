<h2>1. HOMELAB SERVER HARDWARE</h2>

for this project, I used an Intel i5 7600 4 core 3.6ghz processor (totally shitty but does the work).
8 GB RAM will be good. no more required. a 256 GB NVME for booting and storing 2 vms 1 TB and 500 GB for fileserver storage.

<h2>2. DISCLAIMER (PROJECT DESCRIPTION AND FRUSTRATION)</h2>

took me long enough to go through trial and error but the final walkthrough is here. you can host your own fileserver within 3 hrs consisting of a webpage (mine is hosted on Onion site :) don't ask why!), and a Linux machine (I used Parrotsec) to access from any
browser(can have Windows if better hardware, can have gaming purpose windows if have far better hardware).

<h2>4. SETUP</h2>

the whole home lab consists of 2 parts. a Raspberry Pi to remotely turn on the main server and the main server, which we will access as the lab. The Raspi and electronics configuration will be at the end of this write-up. 

<h3>A. Install Ubuntu 22.04 lts as the base OS.</h3>

it is recommended to use the Ubuntu server. easy raid configuration lets us use effectively use multiple drives. but you can't access locally uploaded files in the web browser... damn database doesn't want to scan for files.
anyway, install Ubuntu on the boot drive. leave the rest of your disks alone, we will merge them later.
after installing Ubuntu we have to configure our storage. we will use the rest of our boot storage on nvme for virtualization purposes, and the HDDs for fileserver storage. so let's marge the storage. 
	start by partitioning the disks 
locate disks
>$lsblk
then partition using fdisk
>$sudo fdisk /dev/sda
>m
(will use gpt partition)
>g
and then use the whole disks by pressing enter, then save and exit with:
>w
partition all the drives you want to merge like this

check the partitions
>$lsblk

create filesystem. I will use ext4
>$sudo mkfs.ext4 /dev/sda1
do the same for all drive partition

now create a mount point for disks. I'll use /mnt
>$cd /mnt
>$ll
>$sudo mkdir sda1 sdb1 (as per your disk layout)
now add disk and mount point to fstab to ensure disk will be mounted each time we boot up the server
>$sudo nano /etc/fstab
add:
>/dev/sda1 /mnt/sda1 auto nosuid,nodev,nofail,x-gvfs-show 0 0
>/dev/sdb1 /mnt/sdb1 auto nosuid,nodev,nofail,x-gvfs-show 0 0
now ctrl o ctrlx for save and exit
>$sudo mount -a
now change owner to users
>$sudo chown username:username

now we will install and configure mergerfs
>$sudo apt update && sudo apt install mergerfs -y
>$cd /mnt
>$sudo mkdir myfiles (our merged file will be inside of it)
>$sudo mergerfs -o allow_other,use_ino,cache.files=off,dropcacheonclose=true,category.create=mfs,fsname=myfiles /mnt/sda1:/mnt/sdb1 /mnt/myfiles/
>$sudo nano /etc/fstab
add:
>/mnt/sda1:/mnt/sdb1 /mnt/myfiles fuse.mergerfs allow_other,use_ino,cache.files=off,dropcacheonclose=true,category.create=mfs,fsname=myfiles,nonempty,x-gvfs-show 0 0
save and exit
>$sudo mount -a

now your merged filesystem will be mounted, a reboot will be advised

now we will install nextcloud. a good opensource fileserver.

Install Apache web server by using the below command
>$sudo apt install apache2
Check the status of the Apache web server
>$systemctl status apache2
Install php and dependencies
>$sudo apt-get install php8.1 php8.1-cli php8.1-common php8.1-imap php8.1-redis php8.1-snmp php8.1-xml php8.1-zip php8.1-mbstring php8.1-curl php8.1-gd php8.1-mysql
Install MariaDB server
>$sudo apt install mariadb-server
Check the status of MariaDB
>$systemctl status mariadb

Create a database and grant privileges to the user
>$mysql
>CREATE DATABASE nextcloud;
>GRANT ALL PRIVILEGES ON nextcloud.* TO 'nextcloud'@'localhost' IDENTIFIED BY 'password';
>FLUSH PRIVILEGES;
>exit;
Change into html directory
>$cd /var/www/html
Download the nextcloud by using the wget command
>$sudo wget https://download.nextcloud.com/server/releases/nextcloud-24.0.1.zip
(used this old version. new one has a better ui but I faced some issues)

Extract the file using the unzip command
>$sudo unzip nextcloud-24.0.1.zip
Change the ownership of the file 
>$vim /etc/apache2/sites-available/nextcloud.conf
Paste the following lines in the file and save the file
><VirtualHost *:80>
>ServerName yourdomain.com
>DocumentRoot /var/www/html/nextcloud
><Directory /var/www/html/nextcloud/>
> Require all granted
> Options FollowSymlinks MultiViews
> AllowOverride All
> <IfModule mod_dav.c>
> Dav off
> </IfModule>
></Directory>
>ErrorLog /var/log/apache2/yourdomain.com.error_log
>CustomLog /var/log/apache2/yourdomain.com.access_log common
></VirtualHost>

Enable the Apache2 configuration file 
>$sudo a2ensite nextcloud.conf
Enable the Apache2 Module
>$sudo a2enmod rewrite
Disable the Apache default welcome page 
>$sudo a2dissite 000-default.conf
>$sudo systemctl reload apache2
Check the syntax of conf file
>$sudo apachectl -t
Restart the Apache web server
>systemctl restart apache2

Open the browser and search with IP the web interface will be shown. the username and passewd will be the admin account
data folder. set the path to the merged storage
input database username passwd as set in mariadb
and install

now after installation you will be greeted by the nextcloud admin panel. you can add users and their quota to share storage publicly

as per local file upload and sync I faced a lot of problem. but with this installation you will see nextcloud/data folder in the merged storage.
you can store files locally there and for syncing those data, you have to find a file named occ inside /var/www/html/nextcloud, or according to your installation location then
>$sudo occ files:scan --all
all database will be scanned and synced with web interface


<h3>B. host your fileserver publicly</h3>
awesome so we have our fileserver now. but if we can't access it from outside we can't officially say fuck off to cloud storage services. I used various free tunnelling service but they are made for API testing and offer real pathetic speed. 
rather get a registered domain that will be of so much use. I got one from hostinger.register your domain and we will use cloudflare tunneling service
Before you start, make sure you:
a.Add a website to Cloudflare.
b.Change your domain nameservers to Cloudflare.
changing and authentication of nameservers can take upto 24 hrs. Mine took about 3
Now download and install Cloudflared
Use the apt package manager to install cloudflared on compatible machines.
Add Cloudflare’s package signing key:

>$sudo mkdir -p --mode=0755 /usr/share/keyrings
>$curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null

Add Cloudflare’s apt repo to your apt repositories:

>$echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list

Update repositories and install cloudflared:
>$sudo apt-get update && sudo apt-get install cloudflared
Authenticate cloudflared

>$cloudflared tunnel login

Running this command will:
Open a browser window and prompt you to log in to your Cloudflare account. After logging in to your account, select your hostname.
Generate an account certificate, the cert.pem file, in the default cloudflared directory.
​​Create a tunnel and give it a name

>$cloudflared tunnel create <NAME>

Running this command will:
Create a tunnel by establishing a persistent relationship between the name you provide and a UUID for your tunnel. At this point, no connection is active within the tunnel yet.
Generate a tunnel credentials file in the default cloudflared directory.
Create a subdomain of .cfargotunnel.com.
From the output of the command, take note of the tunnel’s UUID and the path to your tunnel’s credentials file.

Confirm that the tunnel has been successfully created by running:

>$cloudflared tunnel list

​​Create a configuration file
In your .cloudflared directory, create a config.yml file using any text editor. This file will configure the tunnel to route traffic from a given origin to the hostname of your choice.

Add the following fields to the file:

>tunnel: <Tunnel-UUID>
>credentials_file: /root/.cloudflared/<Tunnel-UUID>.json
>ingress:
>  - hostname: subdomain.domain.com
>    service: http://192.168.40.244:80
>  - service: http_status:404 # this is required as a 'catch-all'

Now assign a CNAME record that points traffic to your tunnel subdomain:
>$cloudflared tunnel route dns <UUID or NAME> <hostname>

Confirm that the route has been successfully established:

>$cloudflared tunnel route IP show
Run the tunnel to proxy incoming traffic from the tunnel to any number of services running locally on your origin.

>$cloudflared tunnel run <UUID or NAME>

If your configuration file has a custom name or is not in the .cloudflared directory, add the --config flag and specify the path.

>$cloudflared tunnel --config /path/your-config-file.yml run <UUID or NAME>

You can now route traffic to your tunnel using Cloudflare DNS or determine who can reach your tunnel with Cloudflare Access.

Now you probably don’t want to have to manually run the service every time so we can configure the service to start automatically.
Install service
>$cloudflared service install
Start service
>$systemctl start cloudflared
Enable service
>$systemctl enable cloudflared

now you can officially say fuck you to paid cloud webservers and your cg-nat ed ISP 

<h3>C. wanna host website on dark web?</h3>

ok ok i get it this really sounds cool. but seems hard ain't it? NOPE. it's easy af. let's host one today.
i installed qemu/kvm virtualmanager on ubuntu host and assigned one core and 2 gb ram to a debian virtual machine and set it to boot on startup. 
to install vitualmanager
>$sudo apt install virt-manager
>$sudo virt-manager
if you are fammilar with virtualbox you surely can install a vm here. I trust you. <3
after setting up your vm, and getting debian running, let's host our dark web

Setup Website (nginx) 
Install Ngninx
>$sudo apt install nginx
 
Copy website files to Nginx directory
>$sudo cp -r ~/website /var/www/
 
Edit Nginx default website
>$sudo nano /etc/nginx/sites-available/default (change the path to website path)
 
Change Website location
>$root /var/www/website
 
Test Nginx Config
>$nginx -t
 
Restart Nginx
>$systemctl restart nginx
 
Install ToR
 
Install Pre-Reqs
>$apt install apt-transport-https
 
Cat version
>$cat /etc/debian_version (we will need this later)
 
Create a new file
>$sudo nano /etc/apt/sources.list.d/tor.list
 
Add these two lines of config
**replacing "distribution" with your debian version

>deb [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org <DISTRIBUTION> main
>deb-src [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org <DISTRIBUTION> main
 
Add the GPG Key
>$sudo wget -qO- https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --dearmor | tee /usr/share/keyrings/tor-archive-keyring.gpg >/dev/null

Install ToR
>$sudo apt update
>$sudo apt install tor deb.torproject.org-keyring
 
Configure ToR
>$sudo nano /etc/tor/torrc
 
Uncomment these lines of config

#HiddenserviceDir /var/lib/tor/hidden_service
#HiddenServicePort 80 127.0.0.1:80
 
Restart ToR
>$sudo systemctl restart tor
 
See your onion address
>$cat /var/lib/tor/hidden_service/hostname

now you got your onion address... that's it.. you have now your website on dark web ;0 Sp00ky..

the vm will auto start every time the fileserver boots and so will the tor service.

 <h3>D. personalized linux box</h3>

want a THM or HackTheBox styled attackbox that you can access remotely through browser? I got your back. there are a lot of vnc services and most are bad. so we will take one shot and call a homerun
I used the htb verson of parrotsec. the os really looks cool. install it the same way as the debian. assign 2 core and 4gigs of ram. and install

after installation we will install x11vnc. rest vncs are bad.

>$sudo apt install x11vnc

>$sudo nano /lib/systemd/system/x11vnc.service

Copy and paste these commands - change the password
>[Unit]
>Description=x11vnc service
>After=display-manager.service network.target syslog.target
>
>[Service]
>Type=simple
>ExecStart=/usr/bin/x11vnc -forever -display :0 -auth guess -passwd password
>ExecStop=/usr/bin/killall x11vnc
>Restart=on-failure
>
>[Install]
>WantedBy=multi-user.target

Save file and run these commands:

>$systemctl daemon-reload
>$systemctl enable x11vnc.service
>$systemctl start x11vnc.service
>$sudo systemctl status x11vnc.service

last command will give us the port on which the process is running. its by default 5900

now we will configure cloudflare tunnel to access this over browser 

do same configuration as before. 
the config.yml file should look like this>

>tunnel: <NAME>
>ingress:
>- hostname: subdomain.domain.com
>  service: tcp://localhost:5900
>- service: http_status:404

then Route your Tunnel to your website and Run your Tunnel:

>$cloudflared tunnel --config path/config.yaml run <NAME>

The last step is to create a Zero Trust application to run your VNC server in the Browser.

In Zero Trust, go to Access > Applications.

Select Add an application and choose Self-hosted.

Name the application and set the domain to which you would like to expose the VNC server.
Add an Allow or Block policy. I allowed users with emails ending in @gmail.com and one time pin.

In Additional settings, set Browser rendering to VNC.
Users will see a login screen with your configured identity providers. After successful authentication, they may be prompted to enter the VNC server’s password.

and boom! you have your browser based remote os. just for god's sake don't use chrome!!!

<h3>now for the raspberry pi..</h3>
 before diving in the process of setting up the server and making a webpage.. i couldn't set up the cloudflare tunnel on raspbian 32 bit (legacy). there were multiple errors. So i used remoteit tunneling service. one crutial thing is that from an attacker perspective.. one wouldn't be able to find out the hardware control panel of the server.

let's start.
the main purpose of integrating the pi with the homelab was solely power saving. the 5v 0.5~1 watt pi barely draws any current but can do charms. i used it to sequentially power on 2 relays, one to power on the psu and another for triggering the motherboard power button. in simple words, pi control a circuit with it' GPIO pins that,
if user turns on the switch in webpage,
the circuit is on, the relay for psu switches on
after 3 seconds (wait time for moderboard capacitors to charge up),
the relay for motherboard switches on for 1 sec (replicating switching on a pc)
then turns off
if the user turns off the switch in the webpage,
the relay for motherboard turns on for 1 sec,
then turns off. this initiates shutdown through power button. (we have to make some changes in os settings later)
it takes approx 30 seconds for the os to turn off through this. so with this calc we have alloted 50 seconds to wait and then turn off the relay for the psu.

now let's build this.
first we have to enable the action for pressing the power button. go to settings and search for this action.
after enabling shutdown sequence, we will disable the popup to direct go to shutdown without taking any confirmation from the user.
to do this use this command.
gsettings set org.gnome.SessionManager logout-prompt false
this will disable the logout prompt and make our work easier to automate the whole thing.
now for the webserver.
we used flask and a simple webpage that turns on the server and have 3 buttions to redirect to 1. fileserver, 2.url for darkwepage 3. attackbox access
used GPIO 17 and 18 for triggering the relays.
the code can be found in the repo.
the logic looks like this.

if status=="on":
GPIO.output(17,GPIO.HIGH)
time.sleep(3)
GPIO.output(18, GPIO.HIGH)
time.sleep(0.5)
GPIO.output (18,GPIO. LOW)
if status=="off":
GPIO.output(18, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(18, GPIO. LOW)
time.sleep(50)
GPIO.output(17,GPIO. LOW)

then we have to go to to remote.it and the process after it is simple. if you came this far you can do it.
lastly. for hardware you can use 2 channel relay board. or if you want to build one, you will need a veroboard, 2 relays, 2 1k ohms resistance, 2 2222 or 547 or 337 diode. circuit diagram will be uploaded soon.

That's it Folks.. The End.
