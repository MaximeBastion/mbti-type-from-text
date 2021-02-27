import argparse
import logging
import os

from mbti_type_from_text.db_utils import create_connection, execute_sql_script

logger = logging.getLogger(name="create_db")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--script_path",
        type=str,
        required=True,
        help="Path to a SQL file to initialize the database"
    )
    parser.add_argument(
        "--db_path",
        type=str,
        required=True,
        help="Path to where the database file will be saved"
    )
    args = parser.parse_args()

    if os.path.exists(args.db_path):
        logger.info("The Database already exists at '{}'".format(args.db_path))
    else:
        logger.info("Create connection to '{}'".format(args.db_path))
        db_connection = create_connection(db_path=args.db_path)

        logger.info("Read query from '{}'".format(args.script_path))
        with open(args.script_path, "r") as f:
            sql_script = f.read()

        logger.info("Execute query")
        execute_sql_script(sql_script=sql_script, db_connection=db_connection)

        logger.info("Close connection")
        db_connection.close()
