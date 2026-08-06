### Tool setup over WSL

to start wsl,


```
wsl
```


```
sudo apt update
```

This step will install MySQL 8.x version.

```
sudo apt install -y mysql-server
```

After installation, check version.

```
mysql --version
```

mysql installed as service, it means, when you start wsl, mysql runs automatically

However ensure to enable to start mysql on boot

```
sudo systemctl enable mysql
```

Check if mysql running

```
sudo systemctl status mysql
```

start if not running

```
sudo systemctl start mysql
```

mysql SHOULD NEVER exposed to 0.0.0.0, which listen on all the network interfaces (wifi, ethernets, virtual networks) or any specific interface other than loopback ie 127.0.0.1. No one expected to connect mysql outside your machine strictly during this learning phase.

```
sudo ss -ltnp | grep mysqld
```

Mysql runs on port 3306, 127.0.0.1:3306 where mysql listen to localhost connection, 0.0.0.0:* actually means accept IP, however since it binds to 127.0.0.1, it does not accept over ethernet or wifi connection.

Not a command, just preview.
```
sudo ss -ltnp | grep mysqld
[sudo: authenticate] Password:
LISTEN 0      70          127.0.0.1:33060      0.0.0.0:*    users:(("mysqld",pid=333,fd=21))
LISTEN 0      151         127.0.0.1:3306       0.0.0.0:*    users:(("mysqld",pid=333,fd=24))
```


We have stop | restart commands, along with start command

To set mysql root password,

```
sudo mysql
```

below instruction setup weak password, not a production recommendation.

Here it allow root user to be accepted only through localhost, you cannot connect mysql over other machines.

copy below statement to notepad, edit your password of choice, before run the command

```
ALTER USER 'root'@'localhost'

IDENTIFIED WITH caching_sha2_password

BY 'your-secure-password';



FLUSH PRIVILEGES;

EXIT;
```

check mysql root password successful.

```
mysql -u root -p
```

```
SELECT VERSION();
```

```
SHOW DATABASES;
```

```
EXIT;
```

Advised, not to use *root* for regular connection.


Instead create user of your choice. Copy below to notebook, edit yourname and yourpassword of your choice.


```
mysql -u root -p
```

```
CREATE USER 'yourname'@'localhost'
IDENTIFIED BY 'yourpassword';

FLUSH PRIVILEGES;
```
```
Exit; 
```


To grant permission to a user over a new database. This setup restrict, mysql to accept connection only from localhost 


```
mysql -u root -p
```

*.* refers to database.tables, not a good thing.

```
GRANT ALL PRIVILEGES ON *.* TO 'yourname'@'localhost'
WITH GRANT OPTION;

FLUSH PRIVILEGES;
```

Instead, limit database, objects

```
GRANT ALL PRIVILEGES ON salesdb.* TO 'yourname'@'localhost'
WITH GRANT OPTION;

FLUSH PRIVILEGES;
```

or

ON sales.orders, or any table or view of your preference.

