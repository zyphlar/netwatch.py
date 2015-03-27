NetWatch.py - Turnkey Network Dashboard
=======================================

Requirements
-----------

- nmap

Installation
------------

Install python-nmap and netaddr either via pip or via the below instructions:

```
cd python-nmap-0.3.4
sudo python setup.py install
cd ..
cd netaddr-0.7.10
sudo python setup.py install
cd ..
chmod +x netwatch.py
```

Running
-------

- Manually:

```
./netwatch.py
```

- Automatically login on a Raspberry Pi:
  - `sudo nano /etc/inittab`
  - Navigate to the following line in inittab
    - `1:2345:respawn:/sbin/getty 115200 tty1`
  - Add a # at the beginning of the line to comment it out
    - `#1:2345:respawn:/sbin/getty 115200 tty1`
  - Add the following line just below the commented line
    - `1:2345:respawn:/bin/login -f pi tty1 </dev/tty1 >/dev/tty1 2>&1`
  - This will run the login program with pi user and without any authentication
  - Save and Exit.
    - Press Ctrl+X to exit nano editor followed by Y to save the file and then press Enter to confirm the filename.
  - Reboot the pi and it will boot straight on to the shell prompt pi@raspberrypi without prompting you to enter username or password.
- Run automatically after login:
  - `echo '~/netwatch.py/netwatch.py' > ~/.bash_profile`
