CREATE TABLE `stock` (
  `ticker` varchar(10) NOT NULL,
  `sector` varchar(45) DEFAULT NULL,
  `age` datetime DEFAULT NULL,
  `description` mediumblob,
  PRIMARY KEY (`ticker`)
);

CREATE TABLE `minute_stock_data` (
  `ticker` varchar(10) NOT NULL,
  `datetime` datetime NOT NULL,
  `start_price` float DEFAULT NULL,
  `end_price` float DEFAULT NULL,
  `volume` int DEFAULT NULL,
  `percent_change` float DEFAULT NULL,
  PRIMARY KEY (`ticker`,`datetime`)
);

CREATE TABLE `news` (
  `title` varchar(300) NOT NULL,
  `datetime` datetime NOT NULL,
  `news_url` mediumblob,
  `tickers` mediumblob,
  `newscol` varchar(45) DEFAULT NULL,
  `image_url` mediumblob,
  `text` longblob,
  `source_name` mediumblob,
  `topics` mediumblob,
  `sentiment` varchar(100) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`datetime`,`title`)
);

CREATE TABLE `eps` (
  `ticker` varchar(10) NOT NULL,
  `year` int DEFAULT NULL,
  `quarter` int DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `exp_eps` float DEFAULT NULL,
  `actual_eps` float DEFAULT NULL,
  PRIMARY KEY (`ticker`)
);
daily_data_trend | CREATE TABLE `daily_data_trend` (
  `ticker` varchar(10) NOT NULL,
  `date` datetime NOT NULL,
  `day_movement` float DEFAULT NULL,
  `pre_movement` float DEFAULT NULL,
  `pre_MSE` float DEFAULT NULL,
  `daily_high` float DEFAULT NULL,
  `daily_low` float DEFAULT NULL,
  `daily_start` float DEFAULT NULL,
  `daily_end` float DEFAULT NULL,
  PRIMARY KEY (`ticker`,`date`)
);
