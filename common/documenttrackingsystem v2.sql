-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 12, 2024 at 08:25 AM
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
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `UserID` int(11) NOT NULL,
  `AdminSpecificField` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `documents`
--

CREATE TABLE `documents` (
  `DocNo` int(11) NOT NULL,
  `TrackingNumber` varchar(255) NOT NULL,
  `UserID` int(11) DEFAULT NULL,
  `DocTypeID` int(11) DEFAULT NULL,
  `SchoolID` int(11) DEFAULT NULL,
  `OfficeID` int(11) DEFAULT NULL,
  `DocDetails` text DEFAULT NULL,
  `DocPurpose` varchar(255) DEFAULT NULL,
  `DateEncoded` date DEFAULT NULL,
  `DateReceived` date DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `documents`
--

INSERT INTO `documents` (`DocNo`, `TrackingNumber`, `UserID`, `DocTypeID`, `SchoolID`, `OfficeID`, `DocDetails`, `DocPurpose`, `DateEncoded`, `DateReceived`, `Status`) VALUES
(1, 'MhKTp0tg', 1, 4, 3, 4, 'asda', 'asda', '2024-09-12', NULL, 'Pending');

-- --------------------------------------------------------

--
-- Table structure for table `document_type`
--

CREATE TABLE `document_type` (
  `DocTypeID` int(11) NOT NULL,
  `DocTypeName` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `document_type`
--

INSERT INTO `document_type` (`DocTypeID`, `DocTypeName`) VALUES
(2, 'Advisory'),
(1, 'AIP'),
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
  `OfficeName` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `offices`
--

INSERT INTO `offices` (`OfficeID`, `OfficeName`) VALUES
(1, 'SDO - OSDS - Accounting I'),
(2, 'SDO - OSDS - Accounting II Validators'),
(3, 'SDO - OSDS - Administrative Office'),
(4, 'SDO - OSDS - BAC'),
(6, 'SDO - OSDS - ICT'),
(5, 'SDO - OSDS - Legal');

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `RoleID` int(11) NOT NULL,
  `Rolename` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`RoleID`, `Rolename`) VALUES
(1, 'Admin'),
(3, 'Staff'),
(2, 'User');

-- --------------------------------------------------------

--
-- Table structure for table `schools`
--

CREATE TABLE `schools` (
  `SchoolID` int(11) NOT NULL,
  `SchoolName` varchar(255) NOT NULL
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
-- Table structure for table `staff`
--

CREATE TABLE `staff` (
  `UserID` int(11) NOT NULL,
  `OfficeID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `TransactionID` int(11) NOT NULL,
  `OfficeID` int(11) DEFAULT NULL,
  `DocNo` int(11) DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL,
  `ReceivedDate` date DEFAULT NULL,
  `ProcessDate` date DEFAULT NULL,
  `ForwardDate` date DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL,
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
  `Firstname` varchar(255) DEFAULT NULL,
  `Middlename` varchar(255) DEFAULT NULL,
  `Lastname` varchar(255) DEFAULT NULL,
  `IDNumber` varchar(255) DEFAULT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `Password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`UserID`, `RoleID`, `SchoolID`, `Firstname`, `Middlename`, `Lastname`, `IDNumber`, `Email`, `Password`) VALUES
(1, 2, 3, 'Kyle', 'kai', 'Romarate', '123123', 'kyle@gmail.com', 'scrypt:32768:8:1$1DgnYDnkn5A9V1LJ$43713743caf3c9a7545fbe9c1dc966e614ad85bea350dc535cc3d48928a5751f9f92677baa980cf82e2998b7899fe8a1876a3f2e6ee44a0e91d33e465b140ac7'),
(2, 1, 3, 'jan', 'kai', 'Romarate', '12312345', 'janskai@gmail.com', 'scrypt:32768:8:1$w9q73f2aQXghsUmC$4da0d808bf507d075a8b89d257012f94bd7e20809f7b61ec0f77147c50fa8601ea7306252b9de9fe71d95629c2bb34b382edf21c6884c1a66b42afa2ba52407b'),
(3, 2, 5, 'luigie', 'Am', 'gido', '12893131', 'luigiegido@gmail.com', 'scrypt:32768:8:1$CPNQToFTFUI46f1N$899e70fcb6b02b82f2999ff3dcc953aee8ec9bb477cf0625e5924dc2c71d58409aeeeeeb1b27ef374701da795b8f131b157731ee3d3bfe402461fc59b4553e4f'),
(5, 3, 3, 'staff', 'staff', 'staff', '41412', 'staff@gmail.com', 'scrypt:32768:8:1$Ooz5F9w0IjXryPzt$f544f72d6e7c72a59e6b19eef38e0e9f858e52770395ae9302d4f8f245e93988119259070f1bdf4768180d499b53f3565e4ba74a4854087596e96827549eb69d');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`UserID`);

--
-- Indexes for table `documents`
--
ALTER TABLE `documents`
  ADD PRIMARY KEY (`DocNo`),
  ADD UNIQUE KEY `TrackingNumber` (`TrackingNumber`),
  ADD KEY `UserID` (`UserID`),
  ADD KEY `DocTypeID` (`DocTypeID`),
  ADD KEY `SchoolID` (`SchoolID`),
  ADD KEY `OfficeID` (`OfficeID`);

--
-- Indexes for table `document_type`
--
ALTER TABLE `document_type`
  ADD PRIMARY KEY (`DocTypeID`),
  ADD UNIQUE KEY `DocTypeName` (`DocTypeName`);

--
-- Indexes for table `offices`
--
ALTER TABLE `offices`
  ADD PRIMARY KEY (`OfficeID`),
  ADD UNIQUE KEY `OfficeName` (`OfficeName`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`RoleID`),
  ADD UNIQUE KEY `Rolename` (`Rolename`);

--
-- Indexes for table `schools`
--
ALTER TABLE `schools`
  ADD PRIMARY KEY (`SchoolID`),
  ADD UNIQUE KEY `SchoolName` (`SchoolName`);

--
-- Indexes for table `staff`
--
ALTER TABLE `staff`
  ADD PRIMARY KEY (`UserID`),
  ADD KEY `OfficeID` (`OfficeID`);

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
-- AUTO_INCREMENT for table `documents`
--
ALTER TABLE `documents`
  MODIFY `DocNo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20240015;

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
  MODIFY `RoleID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

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
  MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin`
--
ALTER TABLE `admin`
  ADD CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`);

--
-- Constraints for table `documents`
--
ALTER TABLE `documents`
  ADD CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`),
  ADD CONSTRAINT `documents_ibfk_2` FOREIGN KEY (`DocTypeID`) REFERENCES `document_type` (`DocTypeID`),
  ADD CONSTRAINT `documents_ibfk_3` FOREIGN KEY (`SchoolID`) REFERENCES `schools` (`SchoolID`),
  ADD CONSTRAINT `documents_ibfk_4` FOREIGN KEY (`OfficeID`) REFERENCES `offices` (`OfficeID`);

--
-- Constraints for table `staff`
--
ALTER TABLE `staff`
  ADD CONSTRAINT `staff_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`),
  ADD CONSTRAINT `staff_ibfk_2` FOREIGN KEY (`OfficeID`) REFERENCES `offices` (`OfficeID`);

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
