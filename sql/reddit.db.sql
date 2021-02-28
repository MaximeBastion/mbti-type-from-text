BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Comments" (
	"id"	TEXT NOT NULL UNIQUE,
	"user_id" TEXT NOT NULL,
	"parent_comment_id"	TEXT,
	"title"	TEXT,
	"content"	TEXT NOT NULL,
	"created_datetime"	TEXT NOT NULL,
	"upvotes"	INTEGER NOT NULL,
	"subreddit" TEXT NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "Users"("id"),
	FOREIGN KEY("parent_comment_id") REFERENCES "Comments"("id")
);
CREATE TABLE IF NOT EXISTS "Users" (
	"id"	TEXT NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"flair_text"	TEXT,
	PRIMARY KEY("id")
);
CREATE UNIQUE INDEX IF NOT EXISTS "users_id_index" ON "Users" (
	"id"
);
CREATE INDEX IF NOT EXISTS "comment_user_id_index" ON "Comments" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "comment_id_index" ON "Comments" (
	"id"
);
CREATE INDEX IF NOT EXISTS "comment_datetime_index" ON "Comments" (
	"created_datetime"	ASC
);
COMMIT;
