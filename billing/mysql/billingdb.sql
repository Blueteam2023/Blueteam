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

CREATE TABLE IF NOT EXISTS `Trucks` (
  `id` varchar(10) NOT NULL,
  `provider_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`provider_id`) REFERENCES `Provider`(`id`)
) ENGINE=MyISAM ;

INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('1010', '1');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('2020', '2');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('3030', '3');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('4040', '4');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('5050', '5');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('6060', '6');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('7070', '7');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('8080', '8');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('9090', '9');
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES ('100100', '10');



--
-- Dumping data
--
CREATE TABLE IF NOT EXISTS `transactions` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `datetime` datetime DEFAULT NULL,
  `direction` varchar(10) DEFAULT NULL,
  `truck` varchar(50) DEFAULT NULL,
  `containers` varchar(10000) DEFAULT NULL,
  `bruto` int(12) DEFAULT NULL,
  `truckTara` int(12) DEFAULT NULL,
  --   "neto": <int> or "na" // na if some of containers unknown
  `neto` int(12) DEFAULT NULL,
  `produce` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10001 ;

INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('11110', '20220101150000', 'in', '1010', '5', '2', '50', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('22220', '20220202150000', 'ni', '1010', '5', '2', '50', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('33330', '20220303150000', 'ni', '2020', '5', '2', '20', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('44440', '20220404150000', 'ni', '2020', '5', '2', '20', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('55550', '20220505150000', 'in', '2020', '5', '2', '20', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('66660', '20220606150000', 'ni', '2020', '5', '2', '20', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('77770', '20220707150000', 'ni', '100', '5', '2', '50', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('88880', '20220808150000', 'in', '100', '5', '2', '50', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('99990', '20220909150000', 'in', '100', '5', '2', '50', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('10101010', '20221010150000', 'in', '100', '5', '2', '50', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('11110', '20221111150000', 'in', '1010', '5', '2', '100', '74', '8');
INSERT INTO `transactions` (`id`, `datetime`, `direction`, `trucks`, `containers`, `bruto`, `truckTara`, `neto`, `produce`) VALUES ('22220', '20221212150000', 'ni', '1010', '5', '2', '100', '74', '8');


/*
INSERT INTO Provider (`name`) VALUES ('ALL'), ('pro1'),
(3, 'pro2');

INSERT INTO Rates (`product_id`, `rate`, `scope`) VALUES ('1', 2, 'ALL'),
(2, 4, 'pro1');

INSERT INTO Trucks (`id`, `provider_id`) VALUES ('134-33-443', 2),
('222-33-111', 1);
*/
