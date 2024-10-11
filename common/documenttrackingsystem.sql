-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 11, 2024 at 04:14 AM
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
  `DateEncoded` datetime DEFAULT NULL,
  `DateReceived` datetime DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL,
  `OfficeIDToSend` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `documents`
--

INSERT INTO `documents` (`DocNo`, `TrackingNumber`, `UserID`, `DocTypeID`, `SchoolID`, `OfficeID`, `DocDetails`, `DocPurpose`, `DateEncoded`, `DateReceived`, `Status`, `OfficeIDToSend`) VALUES
(2, 'TRCK-D1MZ-V553-SAN0', 25, 1, NULL, 14, 'asdadsa', 'asdasda', '2024-10-10 10:58:53', NULL, 'Pending', 10),
(3, 'TRCK-AI4L-O462-5WWD', 25, 3, NULL, 14, 'asda', 'sdad', '2024-10-10 11:09:43', NULL, 'Pending', 10),
(4, 'TRCK-6ZL4-5YOE-KXAT', 25, 3, NULL, 14, 'asdas', 'dasdas', '2024-10-10 11:13:45', NULL, 'Pending', 10),
(5, 'TRCK-M995-YAKR-2U8W', 18, 3, NULL, 10, 'asda', 'dasda', '2024-10-10 11:26:59', NULL, 'Pending', 14),
(6, 'TRCK-09ID-AJQ4-MT3A', 18, 2, NULL, 10, 'asda', 'dsada', '2024-10-10 11:27:55', NULL, 'Pending', 9),
(7, 'TRCK-T0IA-KQYH-A9ET', 25, 3, NULL, 14, 'asdasd', 'asdasd', '2024-10-10 11:47:06', NULL, 'Pending', 10),
(8, 'TRCK-HK7J-7XYM-2PSI', 12, 4, 7, 14, 'sadad', 'asdasd', '2024-10-10 11:48:09', NULL, 'Pending', NULL),
(9, 'TRCK-NQKP-TLVE-9T6J', 12, 3, 7, 14, 'weaeq', 'eqeq', '2024-10-10 11:51:32', NULL, 'Pending', NULL),
(10, 'TRCK-7P2Z-Z9H6-MD2Z', 12, 4, 7, 14, 'asdasd', 'asdasda', '2024-10-10 11:56:09', NULL, 'Pending', 14),
(11, 'TRCK-WPU6-SLD7-C1HP', 12, 8, 7, 14, 'gaga', 'agaga', '2024-10-10 11:56:55', NULL, 'Pending', 14),
(12, 'TRCK-1LBB-6X90-4R8F', 25, 3, NULL, 14, 'asdasd', 'asdads', '2024-10-10 11:57:36', NULL, 'Pending', 10),
(13, 'TRCK-8K6B-GAPH-XBOT', 25, 1, NULL, 14, 'ASDA', 'DASDAS', '2024-10-10 13:11:27', NULL, 'Pending', 9),
(14, 'TRCK-YP9J-QB6E-VG32', 25, 1, NULL, 14, 'ASDA', 'DASDAS', '2024-10-10 13:11:29', NULL, 'Pending', 9),
(15, 'TRCK-QE4C-OOZ9-5KLL', 25, 1, NULL, 14, 'ASDA', 'DASDAS', '2024-10-10 13:11:30', NULL, 'Pending', 9),
(16, 'TRCK-VYI2-WSW3-XAGJ', 25, 4, NULL, 14, 'ADA', 'DASDA', '2024-10-10 13:11:42', NULL, 'Pending', 9),
(17, 'TRCK-3USZ-W0TE-ND8P', 25, 8, NULL, 14, 'asdasd', 'asdasda', '2024-10-10 13:36:17', NULL, 'Pending', 14),
(18, 'TRCK-MVJ7-EYAZ-XH1L', 25, 1, NULL, 14, 'test', 'test', '2024-10-10 13:46:23', NULL, 'Pending', 16),
(19, 'TRCK-DFKE-H9W3-NCCT', 25, 1, NULL, 14, 'teste', 'testetete', '2024-10-10 13:52:49', NULL, 'Pending', 10),
(20, 'TRCK-1Z7C-SJ8E-QKHX', 18, 5, NULL, 10, 'gaga', 'gagag', '2024-10-10 14:20:12', NULL, 'Pending', 14),
(21, 'TRCK-TT62-1R0J-TY1M', 18, 5, NULL, 10, 'asdad', 'asdasda', '2024-10-10 14:28:35', NULL, 'Pending', 10),
(22, 'TRCK-2DJC-FSQS-QGLB', 17, 4, NULL, 9, 'asda', 'asdasd', '2024-10-10 15:06:03', NULL, 'Pending', 10),
(23, 'TRCK-79KD-Z5A8-XR9S', 17, 4, NULL, 9, 'asdasd', 'asdasda', '2024-10-10 15:16:07', NULL, 'Pending', 12),
(24, 'TRCK-U9U6-JLTK-QQ4J', 18, 1, NULL, 10, 'asdasdas', 'asdasdasda', '2024-10-10 15:16:48', NULL, 'Pending', 9),
(25, 'TRCK-EJEN-209L-DAAV', 20, 4, NULL, 11, 'asdad', 'agaga', '2024-10-10 15:26:05', NULL, 'Pending', 14),
(26, 'TRCK-6DZJ-779N-VFHE', 21, 5, NULL, 12, 'g', 'a', '2024-10-10 15:30:48', NULL, 'Pending', 9),
(27, 'TRCK-2Q9I-QGI3-2EJ0', 22, 4, NULL, 13, 'fasfa', 'asdasda', '2024-10-10 15:36:14', NULL, 'Pending', 11),
(28, 'TRCK-OVHR-D8H9-6NGI', 23, 2, NULL, 15, 'fa', 'a', '2024-10-10 15:38:42', NULL, 'Pending', 9),
(29, 'TRCK-FTKG-RO55-C08J', 24, 4, NULL, 16, 'g', 'h', '2024-10-10 15:40:57', NULL, 'Pending', 11),
(30, 'TRCK-CC73-PMRZ-V7OL', 20, 3, NULL, 11, 'asda', 'asda', '2024-10-10 15:50:39', NULL, 'Pending', 14),
(31, 'TRCK-GL5H-V5L2-ZRZ9', 17, 3, NULL, 9, 'asdasda', 'dasdasda', '2024-10-10 16:01:00', NULL, 'Pending', 13),
(32, 'TRCK-8OAS-T074-AY1B', 17, 1, NULL, 9, 'aga', 'asdasda', '2024-10-10 16:03:35', NULL, 'Pending', 15),
(33, 'TRCK-2PBW-P41F-A1D3', 17, 2, NULL, 9, 'asdas', '12313', '2024-10-10 16:05:45', NULL, 'Pending', 16),
(34, 'TRCK-ULMA-EK00-U884', 28, 2, NULL, 8, 'asa', 'asdada', '2024-10-10 16:15:22', NULL, 'Pending', 9),
(35, 'TRCK-YR21-YHAB-8CTV', 17, 3, NULL, 9, 'asdasda', 'asdada', '2024-10-10 16:15:38', NULL, 'Pending', 8),
(36, 'TRCK-RSQL-16PI-ISHA', 25, 3, NULL, 14, 'asdasda', 'asdasda', '2024-10-10 16:19:31', NULL, 'Pending', 12),
(37, 'TRCK-SDH2-13GG-BW8D', 25, 3, NULL, 14, 'asdasda', 'asdasda', '2024-10-10 16:19:44', NULL, 'Pending', 12),
(38, 'TRCK-H3GI-9032-S066', 17, 3, NULL, 9, 'asdasda', 'asdasda', '2024-10-10 16:19:57', NULL, 'Pending', 12),
(39, 'TRCK-NQHW-5HWT-1HSK', 23, 3, NULL, 15, 'asdas', 'adasda', '2024-10-10 16:20:28', NULL, 'Pending', 12);

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
(8, 'ADMIN OFFICE'),
(9, 'BUDGET OFFICE'),
(10, 'CASHIER OFFICE'),
(11, 'HRMU OFFICE'),
(12, 'ICT OFFICE'),
(13, 'LEGAL OFFICE'),
(14, 'RECORDS OFFICE'),
(15, 'SCHOOLS DIVISION SUPERINTENDENT OFFICE'),
(16, 'SUPPY OFFICE');

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
(5, 'Busay Elementary School'),
(8, 'Cogon Pardo National High School'),
(7, 'Pardo Elementary School');

-- --------------------------------------------------------

--
-- Table structure for table `staffs`
--

CREATE TABLE `staffs` (
  `UserID` int(11) NOT NULL,
  `OfficeID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `staffs`
--

INSERT INTO `staffs` (`UserID`, `OfficeID`) VALUES
(28, 8),
(17, 9),
(18, 10),
(20, 11),
(21, 12),
(22, 13),
(25, 14),
(23, 15),
(24, 16);

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `TransactionID` int(11) NOT NULL,
  `OfficeID` int(11) DEFAULT NULL,
  `PreviousOfficeID` int(11) DEFAULT NULL,
  `DocNo` int(11) DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL,
  `ForwardedByUserID` int(11) DEFAULT NULL,
  `ReceivedDate` datetime DEFAULT NULL,
  `ProcessDate` datetime DEFAULT NULL,
  `ForwardDate` datetime DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL,
  `TransactionType` varchar(50) DEFAULT NULL,
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
(12, 2, 7, 'user', 'user', 'user', '09123123123', 'user@gmail.com', 'scrypt:32768:8:1$PBVfxpAXvVVQwxZD$0e63c9c4eeec56ca5439799857757e5e6b9b37d73a7680cace9fa9bc45492c719939ab633880e228e9646931b92a4a91d9f8d3272f17d58d4b4ccded640c0fa1'),
(13, 1, 1, 'admin', 'admin', 'admin', '12313123123', 'admin@gmail.com', 'scrypt:32768:8:1$Tc0N0NpFyJkxuoX5$fd5400950bf0f2698f710809cec8204406b58dcf16c933e76f28115332789aa6ceff45bdc77092263073ed188bc72c34e04868843878a64686522af5fb378c2e'),
(14, 3, NULL, 'Records', 'Records', 'Records', '3255151', 'Records@gmail.com', 'scrypt:32768:8:1$2IgqvbOAqLPcV4fU$5364b28e3f7063ea2f3f7860a75f8600a43dd5447936c05784c6df31aa5ecd97d273854952880e9b1d433918c7e26d59eb50bb1ed4059b6deaa7936694d6d7af'),
(17, 3, NULL, 'budget', 'budget', 'budget', '431515121231', 'budget@gmail.com', 'scrypt:32768:8:1$vcUkTR0e9y9yqaMN$db952346852c642312b8593a803ac03d9beb53d84bcaee8777f8d536cecf2221ea69041d7a822cba1222eb0c3221791dd31477b7bf4ca4d638c4c1eed8dc374b'),
(18, 3, NULL, 'cashier', 'cashier', 'cashier', '634543534', 'cashier@gmail.com', 'scrypt:32768:8:1$Y5Pufaqvutioyxku$1380acabf34ad52988c831dbd4ff60e1dc035b281f500f4d0cd2a373ea4a981de0bc552e4469acdae3813a9fa1488c232db8d46446968e39a4afe77cfe13474b'),
(20, 3, NULL, 'hrmu', 'hrmu', 'hrmu', '1231231231', 'hrmu@gmail.com', 'scrypt:32768:8:1$yjsbz9gZS8Xn6toY$33cc6fd3b9e206b7ae8cdb47d4660591c37d61839507480eb721194af3e5e4eba9f1a12b2b029918d33b9e58c22958d4146453bf3a452ff58e045276f3447373'),
(21, 3, NULL, 'ict', 'ict', 'ict', '6454745747', 'ict@gmail.com', 'scrypt:32768:8:1$0YxguIomBGFytSJy$5bf12a1f3a939d87433627c8088e6b54a4bd6c1b5ec2c78720ce21f8c89e6f57f121f6994f373248b1daca8a47808138908301a163283b83f9fc7925e54cde7d'),
(22, 3, NULL, 'legal', 'legal', 'legal', '7568585', 'legal@gmail.com', 'scrypt:32768:8:1$B68ImmoEUQ29r2RS$0f2408e9a25d00b822777c4f8fa72bcaeb6b0432f2c7464a63c4ddbd3a8e53951927920bfce6aba92ed3fb81acc3d41b97962be0cf225ab5b11ab7d0d6e79215'),
(23, 3, NULL, 'sds', 'sds', 'sds', '67969696', 'sds@gmail.com', 'scrypt:32768:8:1$7LVroyHyloWsACGK$7dfe0cba29d37556b3e6f603d5c5a5b9b67dc619ae60c6ef455f1111d0f9d30e2ab745ceed99d7d411d9545b08e267232b191e758580012bf279d8369fc92e5e'),
(24, 3, NULL, 'supply', 'supply', 'supply', '73373573', 'supply@gmail.com', 'scrypt:32768:8:1$0KOW0PD4nsdl79XG$b5be1f876d2e6e5b1a259acd784d4b6a196f961c23b349ab34b1cc4c50268e3885e790ddb1f519e2d3bedff42f6230887d03999d2af65bc152d08e5ee7b4faa9'),
(25, 3, NULL, 'Record', 'Record', 'Record', '346364363', 'Record@gmail.com', 'scrypt:32768:8:1$hoy4w5mWRm8Xw6N9$9888da1b912a6203a58d75576e492c0ebbc953962292ddbeafafc68e30f4ccda0dbcb675a5824ca6fa7e9729a1712e5b9dc9f9eed1babec4f344d38a8a854745'),
(28, 3, NULL, 'admin1', 'admin1', 'admin1', '123123', 'admin1@gmail.com', 'scrypt:32768:8:1$QXMcX4TRHS8T1wsL$3e8951d947d6ed88d96f663ca84790bc5bcec5d4cbb8cc2c935e1efbd5cd49b7e0c23a7e57a32135ff96ccc01d511b326d09a39a404abed3096796f75af2fcbc');

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
  ADD KEY `OfficeID` (`OfficeID`),
  ADD KEY `OfficeIDToSend` (`OfficeIDToSend`);

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
-- Indexes for table `staffs`
--
ALTER TABLE `staffs`
  ADD PRIMARY KEY (`UserID`),
  ADD KEY `OfficeID` (`OfficeID`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`TransactionID`),
  ADD KEY `OfficeID` (`OfficeID`),
  ADD KEY `PreviousOfficeID` (`PreviousOfficeID`),
  ADD KEY `DocNo` (`DocNo`),
  ADD KEY `UserID` (`UserID`),
  ADD KEY `ForwardedByUserID` (`ForwardedByUserID`);

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
  MODIFY `DocNo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20240029;

--
-- AUTO_INCREMENT for table `document_type`
--
ALTER TABLE `document_type`
  MODIFY `DocTypeID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `offices`
--
ALTER TABLE `offices`
  MODIFY `OfficeID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `RoleID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `schools`
--
ALTER TABLE `schools`
  MODIFY `SchoolID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `TransactionID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

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
  ADD CONSTRAINT `OfficeIDToSend` FOREIGN KEY (`OfficeIDToSend`) REFERENCES `offices` (`OfficeID`),
  ADD CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`),
  ADD CONSTRAINT `documents_ibfk_2` FOREIGN KEY (`DocTypeID`) REFERENCES `document_type` (`DocTypeID`),
  ADD CONSTRAINT `documents_ibfk_3` FOREIGN KEY (`SchoolID`) REFERENCES `schools` (`SchoolID`),
  ADD CONSTRAINT `documents_ibfk_4` FOREIGN KEY (`OfficeID`) REFERENCES `offices` (`OfficeID`);

--
-- Constraints for table `staffs`
--
ALTER TABLE `staffs`
  ADD CONSTRAINT `staffs_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`),
  ADD CONSTRAINT `staffs_ibfk_2` FOREIGN KEY (`OfficeID`) REFERENCES `offices` (`OfficeID`);

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`OfficeID`) REFERENCES `offices` (`OfficeID`),
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`PreviousOfficeID`) REFERENCES `offices` (`OfficeID`),
  ADD CONSTRAINT `transactions_ibfk_3` FOREIGN KEY (`DocNo`) REFERENCES `documents` (`DocNo`),
  ADD CONSTRAINT `transactions_ibfk_4` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`),
  ADD CONSTRAINT `transactions_ibfk_5` FOREIGN KEY (`ForwardedByUserID`) REFERENCES `users` (`UserID`);

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
