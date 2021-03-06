-- create database slack;
-- create user slack_user;
-- grant all on slack.* to 'slack_user'@'localhost' identified by 'slack_password';

 -- create necessary game tables
DROP TABLE IF EXISTS `ttt_games`;
CREATE TABLE `ttt_games`(
`id` INT NOT NULL AUTO_INCREMENT,
`channel_id` VARCHAR(15) NOT NULL,
`player1_id` VARCHAR(15) NOT NULL,
`player2_id` VARCHAR(15) NOT NULL,
`current_player` VARCHAR(15) NOT NULL,
`status` INT DEFAULT 1,
`winner` VARCHAR(15) DEFAULT NULL,
`date_created` TIMESTAMP DEFAULT 0,
`date_modified` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `game_moves`;
CREATE TABLE `game_moves`(
`id` INT NOT NULL AUTO_INCREMENT,
`game_id` INT NOT NULL,
`move_number` INT NOT NULL,
`player_id` VARCHAR(15) NOT NULL,
`game_board` VARCHAR(128) NOT NULL,
`date_created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`id`),
KEY `game_index` (`game_id`, `move_number`) USING HASH
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


