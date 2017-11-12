-- Removes the webshop DB
--
-- Author: Andreas Zweili
-- 2017-11-04
-- MariaDB 10.1.26

drop database if exists webshopdb;
drop database if exists test_webshopdb;
drop database if exists django_migrations;
drop user if exists webshop@localhost;
