CREATE DATABASE ISP_MODEM_DB;
GO

USE ISP_MODEM_DB;
GO

CREATE TABLE Modem (
    IdModem INT IDENTITY(1,1) PRIMARY KEY,
    Manufacturer VARCHAR(100),
    Oui VARCHAR(100),
    ProductClass VARCHAR(100),
    JsonParameters VARCHAR(MAX)
);
GO

CREATE TABLE ACServer (
    IdACServer INT IDENTITY(1,1) PRIMARY KEY,
    IdCompany UNIQUEIDENTIFIER,
    ServerAccessIp VARCHAR(100),
    Port VARCHAR(100),
    JsonParameters VARCHAR(MAX),
    IsEnabled BIT,
    DatetimeCreated DATE,
);
GO

CREATE TABLE TermGroup (
    IdTermGroup INT IDENTITY(1,1) PRIMARY KEY,
    NameGroup VARCHAR(100)
);
GO

CREATE TABLE Term (
    IdTerm INT IDENTITY(1,1) PRIMARY KEY,
    IdTermGroup INT,
    Term VARCHAR(100),
    Enable BIT,
    Icon VARCHAR(100),
    FOREIGN KEY (IdTermGroup) REFERENCES TermGroup(IdTermGroup)
);
GO
