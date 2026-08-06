### Tool setup over WSL

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

We have stop | restart commands, along with start command

To set mysql root password,

```
sudo mysql
```

below instruction setup weak password, not a production recommendation.

Here it allow root user to be accepted only through localhost, you cannot connect mysql over other machines.

```
ALTER USER 'root'@'localhost'

IDENTIFIED WITH caching_sha2_password

BY 'root';



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


