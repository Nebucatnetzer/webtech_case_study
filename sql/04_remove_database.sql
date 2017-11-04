-- Removes the webshop DB
--
-- Author: Andreas Zweili
-- 2017-11-04
-- MariaDB 10.1.26

drop database if exists webshopdb;
drop user if exists webshop@localhost;
