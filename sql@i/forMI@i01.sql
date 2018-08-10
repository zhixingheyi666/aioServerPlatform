use fortest;

create table submission_data_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;

create table getClipAction_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;

create table getAccountsData_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;

create table getSmartFilingInfo_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;

create table getFilingInfo_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;


create table getNotebooks_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;

create table getTags_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;

create table setSelectedAccount_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;
