import logging
import sqlite3

logger = logging.getLogger(name="db_utils")


def create_connection(db_path):
    return sqlite3.connect(db_path)


def execute_sql_script(sql_script, db_connection):
    cursor = db_connection.cursor()
    logger.debug("Execute SQL script:")
    logger.debug(sql_script)
    cursor.executescript(sql_script)


def execute_query(query, db_connection):
    cursor = db_connection.cursor()
    logger.debug("Execute query:")
    logger.debug(query)
    cursor.execute(query)


def insert_or_update_user(user_id, user_name, user_flair_text, db_connection):
    query = """
    INSERT INTO Users (id, name, flair_text) 
    VALUES ('{user_id}', '{user_name}', '{user_flair_text}') 
    ON CONFLICT (id) 
    DO UPDATE SET flair_text='{user_flair_text}' 
    WHERE id = '{user_id}' AND (flair_text IS NULL OR flair_text = '')
    """.format(user_id=user_id, user_name=user_name, user_flair_text=user_flair_text)
    execute_query(query=query, db_connection=db_connection)


def insert_or_update_comment(
    comment_id,
    comment_user_id,
    comment_parent_id,
    comment_title,
    comment_content,
    comment_created_datetime,
    comment_upvotes,
    db_connection,
):
    query = """
    INSERT INTO Comments (id, user_id, parent_comment_id, title, content, created_datetime, upvotes) 
    VALUES ('{comment_id}', '{comment_user_id}', '{comment_parent_id}', '{comment_title}', '{comment_content}', '{comment_created_datetime}', {comment_upvotes}) 
    ON CONFLICT (id) 
    DO UPDATE SET title = '{comment_title}', content = '{comment_content}', created_datetime = '{comment_created_datetime}', upvotes = {comment_upvotes} 
    WHERE id = '{comment_id}'
    """.format(
        comment_id=comment_id,
        comment_user_id=comment_user_id,
        comment_parent_id=comment_parent_id,
        comment_title=comment_title,
        comment_content=comment_content,
        comment_created_datetime=comment_created_datetime,
        comment_upvotes=comment_upvotes
    )
    execute_query(query=query, db_connection=db_connection)


def insert_or_update_comment_forest(comments, parent_id, db_connection):
    for comment in comments:
        insert_or_update_comment(
            comment_id=comment.id,
            comment_user_id=comment.author.id,
            comment_parent_id=parent_id,
            comment_title="",
            comment_content=comment.body,
            comment_created_datetime=comment.created_utc,
            comment_upvotes=comment.score,
            db_connection=db_connection,
        )


def insert_or_update_submission(submission, db_connection):
    logger.info("Handle submission '{}' (id='{}')".format(submission.title, submission.id))
    insert_or_update_user(
        user_id=submission.author.id,
        user_name=submission.author.name,
        user_flair_text=submission.author_flair_text,
        db_connection=db_connection
    )
    insert_or_update_comment(
        comment_id=submission.id,
        comment_user_id=submission.author.id,
        comment_parent_id="",
        comment_title=submission.title,
        comment_content=submission.selftext,
        comment_created_datetime=submission.created_utc,
        comment_upvotes=submission.score,
        db_connection=db_connection,
    )
    insert_or_update_comment_forest(comments=submission.comments, parent_id=submission.id, db_connection=db_connection)


def get_all_user_names(db_connection):
    return []


def insert_or_update_user_comments(user, db_connection):
    logger.info("Handle user '{}' (id='{}')".format(user.name, user.id))
