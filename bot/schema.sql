CREATE TABLE `role_assignments` (
    `id`        INTEGER PRIMARY KEY AUTOINCREMENT,
	`user_id`   INTEGER NOT NULL,
	`role_id`   INTEGER NOT NULL,
	FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`),
	UNIQUE (`user_id`, `role_id`) ON CONFLICT FAIL
);
CREATE TABLE `roles` (
    `id`    INTEGER PRIMARY KEY AUTOINCREMENT,
    `name`  TEXT NOT NULL,
	UNIQUE (`name` COLLATE NOCASE)
);
CREATE TABLE `ratings` (
	`id`	    INTEGER PRIMARY KEY AUTOINCREMENT,
	`image_id`  INTEGER NOT NULL,
	`user_id`	INTEGER NOT NULL,
	`rating`	INTEGER NOT NULL,
	`date`      TEXT NOT NULL,
	FOREIGN KEY (`image_id`) REFERENCES `images`(`id`)
);
CREATE TABLE `channel_command_permissions` (
	`channel_id`	INTEGER PRIMARY KEY,
	`command_id`	INTEGER NOT NULL,
	`user_id`   	INTEGER NOT NULL,
	FOREIGN KEY (`command_id`) REFERENCES commands(command_id),
	UNIQUE (`channel_id`, `command_id`) ON CONFLICT REPLACE
);
CREATE TABLE `images` (
	`id`            INTEGER PRIMARY KEY AUTOINCREMENT,
	`file_path`	    TEXT NOT NULL,
	`source`	    TEXT DEFAULT `unknown`,
	`upload_date`   TEXT NOT NULL,
	`uploader`      INTEGER NOT NULL,
	UNIQUE (`file_path` COLLATE NOCASE)
);
CREATE TABLE `commands` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL,
	UNIQUE (`name` COLLATE NOCASE)
);
CREATE TABLE `tags` (
    `id`    INTEGER PRIMARY KEY AUTOINCREMENT,
    `name`  TEXT NOT NULL,
    UNIQUE (`name` COLLATE NOCASE)
);
CREATE TABLE `tag_connections` (
    `link_id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `image_id`  INTEGER NOT NULL,
    `tag_id`    INTEGER NOT NULL,
    FOREIGN KEY (`image_id`) REFERENCES images(`id`),
    FOREIGN KEY (`tag_id`) REFERENCES tags(`id`),
    UNIQUE (`image_id`, `tag_id`)
);