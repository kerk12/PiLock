# PiLock Client
### A homemade Raspberry Pi & Arduino Controlled Door lock mechanism.
Developed by Kyriakos Giannakis (kerk12gr@gmail.com).

### Licence:


### Install:
1. ```git clone --recursive https://github.com/kerk12/PiLock```

2. Run the first setup script as root. This will install all the required stuff including apache, wsgi, pip, along with all the required python libraries needed for the server to function.
```
cd PiLock
chmod 777 setup_apache.sh
sudo ./setup_apache.sh
```
When done, a new SSL certificate, along with its private key will be generated and stored within /etc/apache2/ssl. You will need to connect it with apache. See [here](https://hallard.me/enable-ssl-for-apache-server-in-5-minutes/) for more.

3. Now run the wsgi setup script as root. This will copy the wsgi configuration file to the main apache configuration folder.
```
chmod 777 setup_wsgi.sh
sudo ./setup_wsgi.sh
```
It will also initialize the default database used by the server, create a new superuser (used when managing the server with the admin CP) and last but not least, will add the user www-data to the dialout group. This is needed for accessing the Serial Port of the RPi.
4. Your system will now be restarted.

5. After your system has restarted, navigate to:
```
https://<your_rpi_ip>
```
You should see an SSL warning on your browser. Allow it (we are using a self-signed certificate so this is to be expected).

6. Now you will need to export your SSL Certificate to a file, and name it pilock.crt. This is used when authenticating with the [app](https://github.com/kerk12/PiLockApp). You can export it by either using [this method](https://superuser.com/questions/97201/how-to-save-a-remote-server-ssl-certificate-locally-as-a-file), or via your browser. 