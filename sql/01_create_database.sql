-- Creates the webshop DB
--
-- Author: Andreas Zweili
-- 2017-11-04
-- MariaDB 10.1.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

create database if not exists webshopdb;
grant all on webshopdb.* to
    'webshop'@'localhost'
    identified by '2YKtY53F3HDDzPyExAaSh3jdVNh6VN';
grant all on test_webshopdb.* to
    'webshop'@'localhost'
    identified by '2YKtY53F3HDDzPyExAaSh3jdVNh6VN';
grant all on django_migrations.* to
    'webshop'@'localhost'
    identified by '2YKtY53F3HDDzPyExAaSh3jdVNh6VN';
flush privileges;
