-- create games table
create table `games`(
`id` INT NOT NULL,
`channel_id` VARCHAR(15) NOT NULL,
`player1_id` VARCHAR(15) NOT NULL,
`player2_id` VARCHAR(15) NOT NULL,
`current_turn` VARCHAR(15) NOT NULL,
`status` INT DEFAULT 1,
`winner` VARCHAR(15) DEFAULT NULL,
`date_created` TIMESTAMP DEFAULT 0,
`date_modified` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
