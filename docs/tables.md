## Cobra数据流转流程

Auth - API-KEY
```
CREATE TABLE `auth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(52) NOT NULL,
  `key` varchar(256) NOT NULL,
  `status` tinyint(4) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
Ext - Extensions distribution statistics
```
CREATE TABLE `ext` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` int(11) DEFAULT NULL,
  `ext` varchar(32) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`,`ext`),
  KEY `ix_ext_task_id` (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

Languages - Language and extensions table
```
CREATE TABLE `languages` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `language` varchar(11) NOT NULL,
  `extensions` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_languages_language` (`language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

Projects - Project Information Sheet
```
CREATE TABLE `projects` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `repository` varchar(512) NOT NULL,
  `url` varchar(512) NOT NULL DEFAULT '',
  `name` varchar(50) NOT NULL,
  `framework` varchar(32) NOT NULL DEFAULT '',
  `author` varchar(50) NOT NULL,
  `pe` varchar(32) NOT NULL DEFAULT '',
  `remark` varchar(512) NOT NULL DEFAULT '',
  `last_scan` datetime NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
```

Results - Scan Result Table
```
CREATE TABLE `results` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `task_id` int(11) NOT NULL,
  `rule_id` int(11) NOT NULL,
  `file` varchar(512) NOT NULL,
  `line` int(11) NOT NULL,
  `code` varchar(512) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_task_id_rule_id` (`task_id`,`rule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

Rules - Scan Rule Table
```
CREATE TABLE `rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vul_id` tinyint(4) DEFAULT NULL,
  `language` tinyint(4) DEFAULT NULL,
  `regex_location` varchar(512) NOT NULL DEFAULT '',
  `regex_repair` varchar(512) NOT NULL DEFAULT '',
  `block_repair` tinyint(2) NOT NULL,
  `description` varchar(256) NOT NULL,
  `repair` varchar(512) NOT NULL,
  `status` tinyint(2) NOT NULL,
  `level` tinyint(2) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_rules_vul_id` (`vul_id`),
  KEY `ix_rules_language` (`language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

Tasks - Scan the task table
```
CREATE TABLE `tasks` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `target` varchar(255) NOT NULL,
  `branch` varchar(64) NOT NULL,
  `scan_way` smallint(6) NOT NULL,
  `new_version` varchar(40) NOT NULL,
  `old_version` varchar(40) NOT NULL,
  `time_consume` int(11) NOT NULL,
  `time_start` int(11) NOT NULL,
  `time_end` int(11) NOT NULL,
  `file_count` int(11) NOT NULL,
  `code_number` int(11) NOT NULL,
  `status` tinyint(4) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_tasks_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

User - Administrator account password table
```
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `password` varchar(256) NOT NULL,
  `role` tinyint(2) NOT NULL,
  `last_login_time` datetime NOT NULL,
  `last_login_ip` varchar(16) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

Vuls - Vulnerability Type Table
```
CREATE TABLE `vuls` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(56) NOT NULL,
  `description` varchar(512) NOT NULL,
  `repair` varchar(512) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

Whitelist - White list
```
CREATE TABLE `whitelist` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `rule_id` int(11) NOT NULL,
  `path` varchar(512) NOT NULL,
  `reason` varchar(512) NOT NULL,
  `status` tinyint(4) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_project_id_rule_id` (`project_id`,`rule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```