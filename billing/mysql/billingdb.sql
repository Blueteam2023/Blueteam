--
-- Database: `billdb`
--

CREATE DATABASE IF NOT EXISTS `billdb`;
USE `billdb`;

-- --------------------------------------------------------

--
-- Table structure
--

CREATE TABLE IF NOT EXISTS `Provider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  AUTO_INCREMENT=10001 ;

CREATE TABLE IF NOT EXISTS `Rates` (
  `product_id` varchar(50) NOT NULL,
  `rate` int(11) DEFAULT 0,
  `scope` varchar(50) DEFAULT NULL,
  FOREIGN KEY (scope) REFERENCES `Provider`(`id`)
) ENGINE=MyISAM ;

INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Navel', '50', 'All');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Blood', '50', 'All');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Mandarin', '50', 'All');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Shamuti', '50', 'All');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Tangerine', '50', 'All');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Clementine', '100', 'All');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Grapefruit', '100', 'All');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Valencia', '100', 'All');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Mandarin', '100', '43');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Mandarin', '100', '45');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Tangerine', '80', '12');
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES ('Valencia', '80', '45');

CREATE TABLE IF NOT EXISTS `Trucks` (
  `id` varchar(10) NOT NULL,
  `provider_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`provider_id`) REFERENCES `Provider`(`id`)
) ENGINE=MyISAM ;
--
-- Dumping data
--

/*
INSERT INTO Provider (`name`) VALUES ('ALL'), ('pro1'),
(3, 'pro2');

INSERT INTO Rates (`product_id`, `rate`, `scope`) VALUES ('1', 2, 'ALL'),
(2, 4, 'pro1');

INSERT INTO Trucks (`id`, `provider_id`) VALUES ('134-33-443', 2),
('222-33-111', 1);
*/
