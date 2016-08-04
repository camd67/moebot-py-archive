BEGIN TRANSACTION;
CREATE TABLE `users` (
	`user_id`	    INTEGER PRIMARY KEY,
	`mention`	    TEXT NOT NULL,
	`display_name`	TEXT NOT NULL
);
CREATE TABLE `ratings` (
	`id`	    INTEGER PRIMARY KEY AUTOINCREMENT,
	`user_id`	INTEGER NOT NULL,
	`rating`	INTEGER NOT NULL,
	FOREIGN KEY(`id`) REFERENCES `images`(`id`),
	FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`)
);
CREATE TABLE `channel_command_permissions` (
	`channel_id`	INTEGER PRIMARY KEY,
	`command_id`	INTEGER NOT NULL,
	`user_id`   	INTEGER NOT NULL,
	FOREIGN KEY(`channel_id`) REFERENCES channels(channel_id),
	FOREIGN KEY(`command_id`) REFERENCES commands(command_id),
	UNIQUE (`channelId`, `commandId`) ON CONFLICT REPLACE
);
CREATE TABLE `images` (
	`id`        INTEGER PRIMARY KEY AUTOINCREMENT,
	`filepath`	TEXT NOT NULL UNIQUE,
	`source`	TEXT DEFAULT `unknown`,
	`tags`	    TEXT NOT NULL,
	PRIMARY KEY(int)
);
CREATE TABLE `commands` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL UNIQUE
);
CREATE TABLE `channels` (
	`channel_id`    INTEGER PRIMARY KEY
);
CREATE TABLE `tags` (
    `id`    INTEGER PRIMARY KEY AUTOINCREMENT,
    `name`  TEXT NOT NULL
);
CREATE TABLE `tag_connections` (
    `link_id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `image_id`  INTEGER NOT NULL,
    `tag_id`    INTEGER NOT NULL,
    FOREIGN KEY(`image_id`) REFERENCES images(`id`),
    FOREIGN KEY(`tag_id`) REFERENCES tags(`id`)
);
COMMIT;
