-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 05, 2024 at 11:24 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `documenttrackingsystem`
--

-- --------------------------------------------------------

--
-- Table structure for table `documents`
--

CREATE TABLE `documents` (
  `DocNo` varchar(20) NOT NULL,
  `UserID` int(11) DEFAULT NULL,
  `DocTypeID` int(11) DEFAULT NULL,
  `SchoolID` int(11) DEFAULT NULL,
  `OfficeID` int(11) DEFAULT NULL,
  `DocDetails` text DEFAULT NULL,
  `DocPurpose` text DEFAULT NULL,
  `DateEncoded` datetime NOT NULL,
  `DateReceived` datetime DEFAULT NULL,
  `Status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `document_type`
--

CREATE TABLE `document_type` (
  `DocTypeID` int(11) NOT NULL,
  `DocTypeName` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `document_type`
--

INSERT INTO `document_type` (`DocTypeID`, `DocTypeName`) VALUES
(1, 'AIP'),
(2, 'Advisory'),
(3, 'Application Letter'),
(4, 'Authority to Travel'),
(5, 'Division Clearance'),
(6, 'Job Order'),
(7, 'Leave Application'),
(8, 'Legal Documents');

-- --------------------------------------------------------

--
-- Table structure for table `offices`
--

CREATE TABLE `offices` (
  `OfficeID` int(11) NOT NULL,
  `OfficeName` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `offices`
--

INSERT INTO `offices` (`OfficeID`, `OfficeName`) VALUES
(1, 'SDO - OSDS - Accounting I'),
(2, 'SDO - OSDS - Accounting II Validators'),
(3, 'SDO - OSDS - Administrative Office'),
(4, 'SDO - OSDS - BAC'),
(5, 'SDO - OSDS - Legal'),
(6, 'SDO - OSDS - ICT');

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `RoleID` int(11) NOT NULL,
  `RoleName` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`RoleID`, `RoleName`) VALUES
(1, 'Admin'),
(2, 'Teacher');

-- --------------------------------------------------------

--
-- Table structure for table `schools`
--

CREATE TABLE `schools` (
  `SchoolID` int(11) NOT NULL,
  `SchoolName` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `schools`
--

INSERT INTO `schools` (`SchoolID`, `SchoolName`) VALUES
(1, 'Abellana National School'),
(2, 'Alaska Night High School'),
(3, 'Babag Integrated School'),
(4, 'Bonbon Elementary School'),
(5, 'Busay Elementary School');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `TransactionID` int(11) NOT NULL,
  `OfficeID` int(11) DEFAULT NULL,
  `DocNo` varchar(20) DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL,
  `ReceivedDate` datetime DEFAULT NULL,
  `ProcessDate` datetime DEFAULT NULL,
  `ForwardDate` datetime DEFAULT NULL,
  `Status` varchar(50) NOT NULL,
  `Comments` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `UserID` int(11) NOT NULL,
  `RoleID` int(11) DEFAULT NULL,
  `SchoolID` int(11) DEFAULT NULL,
  `Firstname` varchar(50) NOT NULL,
  `Middlename` varchar(50) DEFAULT NULL,
  `Lastname` varchar(50) NOT NULL,
  `IDNumber` varchar(20) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`UserID`, `RoleID`, `SchoolID`, `Firstname`, `Middlename`, `Lastname`, `IDNumber`, `Email`, `Password`) VALUES
(2, 2, 1, 'Kyle', 'Piko', 'Romarate', '123123', 'kyle@gmail.com', 'scrypt:32768:8:1$cELY6qxP8qFIXxb9$e06a850cbedfebcb9730c0f56e504c9d2118612a768601ec0d504ef30fab966429b68197edbccc3cb1b483eb45920fb9122e8cd22c08ec1e5ed85dac41a6ee51'),
(4, 2, 1, 'jan', 'is', 'kai', '321', 'janskai@gmail.com', 'scrypt:32768:8:1$ra34MwLq86YibFTj$27d661851f7812834b595253b06d5a4dcd98de4cac2689fda9c923f66d5114e9e53ea0f17276909061e0a3ac729003d19dcf86af73b2267297a7eb8f6faf71ef'),
(5, 2, 1, 'lo', 'ui', 'ie', '987', 'louie@gmail.com', 'scrypt:32768:8:1$I5Gqc38TFNmb4Vwj$ff8774c5e26cd4e9824170134bee38a6382b8144f58147520bbdf0aa8cf6263b35b0a836e85175a941034778a6f16005d4448790aad97fa0761d6328c567ca6f'),
(7, 2, 1, 'Kyle', 'Piko', 'Romarate', '1231234', 'kyle1@gmail.com', 'scrypt:32768:8:1$G9pf8zPBv3xkbW1s$e99f835133a9ebe0ee3e9b695a8e92b59fc307c14fda032bb3f40f1e11e0109d98ae501a187453e117f53d3c59e103adbf1088fc8aca37d9df2b7000027baf0b');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `documents`
--
ALTER TABLE `documents`
  ADD PRIMARY KEY (`DocNo`),
  ADD KEY `UserID` (`UserID`),
  ADD KEY `DocTypeID` (`DocTypeID`),
  ADD KEY `SchoolID` (`SchoolID`),
  ADD KEY `OfficeID` (`OfficeID`);

--
-- Indexes for table `document_type`
--
ALTER TABLE `document_type`
  ADD PRIMARY KEY (`DocTypeID`);

--
-- Indexes for table `offices`
--
ALTER TABLE `offices`
  ADD PRIMARY KEY (`OfficeID`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`RoleID`);

--
-- Indexes for table `schools`
--
ALTER TABLE `schools`
  ADD PRIMARY KEY (`SchoolID`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`TransactionID`),
  ADD KEY `OfficeID` (`OfficeID`),
  ADD KEY `DocNo` (`DocNo`),
  ADD KEY `UserID` (`UserID`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`UserID`),
  ADD UNIQUE KEY `IDNumber` (`IDNumber`),
  ADD UNIQUE KEY `Email` (`Email`),
  ADD KEY `RoleID` (`RoleID`),
  ADD KEY `SchoolID` (`SchoolID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `document_type`
--
ALTER TABLE `document_type`
  MODIFY `DocTypeID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `offices`
--
ALTER TABLE `offices`
  MODIFY `OfficeID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `RoleID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `schools`
--
ALTER TABLE `schools`
  MODIFY `SchoolID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `TransactionID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `documents`
--
ALTER TABLE `documents`
  ADD CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`),
  ADD CONSTRAINT `documents_ibfk_2` FOREIGN KEY (`DocTypeID`) REFERENCES `document_type` (`DocTypeID`),
  ADD CONSTRAINT `documents_ibfk_3` FOREIGN KEY (`SchoolID`) REFERENCES `schools` (`SchoolID`),
  ADD CONSTRAINT `documents_ibfk_4` FOREIGN KEY (`OfficeID`) REFERENCES `offices` (`OfficeID`);

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`OfficeID`) REFERENCES `offices` (`OfficeID`),
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`DocNo`) REFERENCES `documents` (`DocNo`),
  ADD CONSTRAINT `transactions_ibfk_3` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`RoleID`) REFERENCES `roles` (`RoleID`),
  ADD CONSTRAINT `users_ibfk_2` FOREIGN KEY (`SchoolID`) REFERENCES `schools` (`SchoolID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
