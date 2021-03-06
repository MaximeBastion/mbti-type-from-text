import logging
import sqlite3
from datetime import datetime

import pandas as pd
from praw.models import MoreComments
from prawcore import NotFound

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
    db_connection.commit()


def insert_or_update_user(user_id, user_name, user_flair_text, db_connection):
    query = """
    INSERT INTO Users (id, name, flair_text) 
    VALUES ('{user_id}', '{user_name}', '{user_flair_text}') 
    ON CONFLICT (id) 
    DO UPDATE SET flair_text='{user_flair_text}' 
    WHERE id = '{user_id}' AND (flair_text IS NULL OR flair_text = '')
    """.format(
        user_id=user_id,
        user_name=user_name.replace("'", "''"),
        user_flair_text=user_flair_text.replace("'", "''") if user_flair_text is not None else "<<NULL>>",
    )
    query = query.replace("'<<NULL>>'", "NULL")
    execute_query(query=query, db_connection=db_connection)


def format_date_for_db(created_utc):
    # created_utc is UNIX
    # SQLite expects dates in format 'YYYY-MM-DD HH:MM:SS'
    dt = datetime.fromtimestamp(created_utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def insert_or_update_comment(
    comment_id,
    comment_user_id,
    parent_submission_id,
    parent_comment_id,
    comment_title,
    comment_content,
    comment_created_utc,
    comment_upvotes,
    subreddit_display_name,
    submission_flair_text,
    db_connection,
):
    query = """
    INSERT INTO Comments (id, user_id, parent_submission_id, parent_comment_id, title, content, created_datetime, upvotes, subreddit, submission_flair_text) 
    VALUES ('{comment_id}', '{comment_user_id}', '{parent_submission_id}', '{parent_comment_id}', '{comment_title}', '{comment_content}', '{comment_created_datetime}', {comment_upvotes}, '{subreddit_display_name}', '{submission_flair_text}') 
    ON CONFLICT (id) 
    DO UPDATE SET title = '{comment_title}', content = '{comment_content}', created_datetime = '{comment_created_datetime}', upvotes = {comment_upvotes} 
    WHERE id = '{comment_id}'
    """.format(
        comment_id=comment_id,
        comment_user_id=comment_user_id,
        parent_submission_id=parent_submission_id,
        parent_comment_id=parent_comment_id if parent_comment_id is not None else "<<NULL>>",
        comment_title=comment_title.replace("'", "''") if comment_title is not None else "<<NULL>>",
        comment_content=comment_content.replace("'", "''"),
        comment_created_datetime=format_date_for_db(created_utc=comment_created_utc),
        comment_upvotes=comment_upvotes,
        subreddit_display_name=subreddit_display_name.replace("'", "''"),
        submission_flair_text=submission_flair_text.replace("'", "''")
        if submission_flair_text is not None and submission_flair_text != ""
        else "<<NULL>>",
    )
    query = query.replace("'<<NULL>>'", "NULL")
    execute_query(query=query, db_connection=db_connection)


def is_user_defined(user):
    if user is None:
        return False
    else:
        try:
            hasattr(user, "id")
        except NotFound as e:
            return False
        return hasattr(user, "id")


def insert_or_update_comment_forest(comments, parent_id, db_connection):
    for comment in comments:
        if isinstance(comment, MoreComments):
            insert_or_update_comment_forest(
                comments=comment.comments(), parent_id=parent_id, db_connection=db_connection
            )
        else:
            if is_user_defined(user=comment.author):
                insert_or_update_user(
                    user_id=comment.author.id,
                    user_name=comment.author.name,
                    user_flair_text=comment.author_flair_text if comment.author_flair_text is not None else None,
                    db_connection=db_connection,
                )
                insert_or_update_comment(
                    comment_id=comment.id,
                    comment_user_id=comment.author.id,
                    parent_submission_id=comment.submission.id,
                    parent_comment_id=parent_id,
                    comment_title=None,
                    comment_content=comment.body,
                    comment_created_utc=comment.created_utc,
                    comment_upvotes=comment.score,
                    subreddit_display_name=comment.subreddit.display_name,
                    submission_flair_text=comment.submission.link_flair_text,
                    db_connection=db_connection,
                )
            else:
                logger.warning("Comment without author (id='{}', parent_id='{}')".format(comment.id, parent_id))
            assert hasattr(comment, "id") and comment.id is not None
            assert hasattr(comment, "replies") and comment.replies is not None
            insert_or_update_comment_forest(comments=comment.replies, parent_id=comment.id, db_connection=db_connection)


def insert_or_update_submission(submission, db_connection):
    parent_id = None
    if is_user_defined(user=submission.author):
        insert_or_update_user(
            user_id=submission.author.id,
            user_name=submission.author.name,
            user_flair_text=submission.author_flair_text if submission.author_flair_text is not None else None,
            db_connection=db_connection,
        )
        insert_or_update_comment(
            comment_id=submission.id,
            comment_user_id=submission.author.id,
            parent_submission_id=submission.id,
            parent_comment_id=None,
            comment_title=submission.title,
            comment_content=submission.selftext,
            comment_created_utc=submission.created_utc,
            comment_upvotes=submission.score,
            subreddit_display_name=submission.subreddit.display_name,
            submission_flair_text=submission.link_flair_text,
            db_connection=db_connection,
        )
        parent_id = submission.id
    else:
        logger.warning("Submission without author (id='{}')".format(submission.id))
    assert hasattr(submission, "id") and submission.id is not None
    assert hasattr(submission, "comments") and submission.comments is not None
    insert_or_update_comment_forest(comments=submission.comments, parent_id=parent_id, db_connection=db_connection)


def get_all_user_names(db_connection):
    return pd.read_sql("SELECT name FROM Users", con=db_connection)["name"].tolist()


def insert_or_update_user_submissions(user, n_hot, db_connection):
    for n, submission in enumerate(user.submissions.hot(limit=n_hot)):
        logger.info("Submission {}/{} of user '{}'".format(n + 1, n_hot, user.name))
        insert_or_update_comment(
            comment_id=submission.id,
            comment_user_id=submission.author.id,
            parent_submission_id=submission.id,
            parent_comment_id=None,
            comment_title=submission.title,
            comment_content=submission.selftext,
            comment_created_utc=submission.created_utc,
            comment_upvotes=submission.score,
            subreddit_display_name=submission.subreddit.display_name,
            submission_flair_text=submission.link_flair_text,
            db_connection=db_connection,
        )


def insert_or_update_user_comments(user, n_hot, db_connection):
    for n, comment in enumerate(user.comments.hot(limit=n_hot)):
        logger.info("Comment {}/{} of user '{}'".format(n + 1, n_hot, user.name))
        insert_or_update_comment(
            comment_id=comment.id,
            comment_user_id=comment.author.id,
            parent_submission_id=comment.submission.id,
            parent_comment_id=None,
            comment_title=None,
            comment_content=comment.body,
            comment_created_utc=comment.created_utc,
            comment_upvotes=comment.score,
            subreddit_display_name=comment.subreddit.display_name,
            submission_flair_text=comment.submission.link_flair_text,
            db_connection=db_connection,
        )
