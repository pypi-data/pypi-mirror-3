
Jabbercracky provides a general-purpose hash-cracking web service for Ubuntu.

--------------------
External requirements: 
- MySQLdb
- oclHashcat-lite from http://hashcat.net/oclhashcat-lite/
- rcracki_mt
- mysql server available
- rainbow tables

--------------------
Database Setup:

*note*  Please remember to put the database and user info from this step
        into /etc/jcrack.conf

1) create a new database, for example 'celery':
mysql> CREATE DATABASE celery;
Query OK, 1 row affected (0.02 sec)

2) grant privileges on that database to a new user:
mysql> GRANT ALL ON celery TO 'celery' IDENTIFIED BY 'YOUR_PASSWORD_HERE';
Query OK, 0 rows affected (0.13 sec)

mysql> FLUSH PRIVILEGES;
Query OK, 0 rows affected (0.05 sec)


3) change the transaction level of the database (mandatory):
mysql> USE celery;
Database changed
 
mysql> SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
Query OK, 0 rows affected (0.00 sec)

-------------------
Configuration:

Please copy the distribution file /etc/jcrack.conf.dist 
to /etc/jcrack.conf and fill in the correct information
for database, db user, and which rainbow tables you have.


-------------------
Running:

On Ubuntu, try:
service jcrackd start

To debug, try:
sh -x /etc/init.d/jcrackd start


---------------------------*
Questions?  awgh@awgh.org
