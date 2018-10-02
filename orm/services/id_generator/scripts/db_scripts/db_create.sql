SET sql_notes=0;

USE orm;

CREATE TABLE if not exists `uuids` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) NOT NULL,
  `uuid_type` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid_idx` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
