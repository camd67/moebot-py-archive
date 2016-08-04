BEGIN TRANSACTION;
CREATE TABLE "users" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`discordId`	INT NOT NULL UNIQUE,
	`name`	TEXT NOT NULL,
	`mention`	TEXT NOT NULL,
	`displayName`	TEXT NOT NULL
);
CREATE TABLE "ratings" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`imageId`	INT NOT NULL,
	`userId`	INT NOT NULL,
	`rating`	INT NOT NULL,
	FOREIGN KEY(`imageId`) REFERENCES `image`(`id`),
	FOREIGN KEY(`userId`) REFERENCES `user`(`id`)
);
CREATE TABLE `channel_command_permissions` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`channelId`	INTEGER NOT NULL,
	`commandId`	INTEGER NOT NULL,
	`permitBy`	INTEGER NOT NULL,
	FOREIGN KEY(`channelId`) REFERENCES channel(id),
	FOREIGN KEY(`commandId`) REFERENCES command(id),
	UNIQUE (`channelId`, `commandId`) ON CONFLICT REPLACE
);
CREATE TABLE "images" (
	`int`	id,
	`filepath`	TEXT NOT NULL UNIQUE,
	`source`	TEXT DEFAULT 'unknown',
	`tags`	TEXT NOT NULL,
	PRIMARY KEY(int)
);
CREATE TABLE "commands" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL UNIQUE
);
CREATE TABLE "channels" (
	`id`	INTEGER UNIQUE,
	PRIMARY KEY(id)
);
COMMIT;
