BEGIN TRANSACTION;
CREATE TABLE `UserRole` (
    `roleId` INTEGER,
    `userId` INTEGER,
    PRIMARY KEY(roleId,UserId),
    FOREIGN KEY (roleId) REFERENCES Role(id),
    FOREIGN KEY (userId) REFERENCES User(id)
);
CREATE TABLE `User` (
    `id` INTEGER PRIMARY KEY,
    `username` TEXT
);
CREATE TABLE `Tag` (
    `id` INTEGER PRIMARY KEY,
    `name` TEXT
);
CREATE TABLE `Role` (
    `id` INTEGER PRIMARY KEY,
    `name` TEXT,
    `permissionLevel` INTEGER UNIQUE
);
CREATE TABLE `PermittedCommand` (
    `id` INTEGER PRIMARY KEY,
    `commandName` TEXT,
    `channelId` INTEGER,
    FOREIGN KEY (channelId) REFERENCES Channel(id)
);
CREATE TABLE `ImageTag` (
    `imageId` INTEGER,
    `tagId` INTEGER,
    PRIMARY KEY (ImageId, TagId),
    FOREIGN KEY (imageId) REFERENCES Image(id),
    FOREIGN KEY (tagId) REFERENCES Tag(id)
);
CREATE TABLE `Image` (
    `id` INTEGER PRIMARY KEY,
    `guid` TEXT,
    `submitterId` INTEGER,
    `caption` TEXT,
    `qualityRating` INTEGER,
    `channelId` INTEGER,
    `postDate` INTEGER,
    `hash` TEXT,
    FOREIGN KEY (submitterId) REFERENCES User(id),
    FOREIGN KEY (channelId) REFERENCES Channel(id)
);
CREATE TABLE `Channel` (
    `id` INTEGER PRIMARY KEY,
    `name` INTEGER
);
COMMIT;
