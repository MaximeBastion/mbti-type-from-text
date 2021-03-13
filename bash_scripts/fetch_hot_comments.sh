#!/usr/bin/env bash
set -e

if [ $# -ne 3 ]; then
  echo "Expected 3 input arguments: bash bash_scripts/fetch_hot_comments.sh <DB_PATH> <REDDIT_CLIENT_ID> <REDDIT_CLIENT_SECRET>"
  exit 1
fi

DB_PATH=$1
REDDIT_CLIENT_ID=$2
REDDIT_CLIENT_SECRET=$3

# https://www.reddit.com/r/infj/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 190 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit infj \
--submission_flairs "Ask INFJs" "What do you think?*" "Personality Theory" "Self Improvement*" "Mental Health"

# https://www.reddit.com/r/intj/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 110 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit intj \
--submission_flairs "Discussion" "Advice" "Question" "MBTI" "Relationship"

# https://www.reddit.com/r/isfp/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 170 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit isfp

# https://www.reddit.com/r/istp/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 140 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit istp

# https://www.reddit.com/r/INTP/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 180 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit INTP

# https://www.reddit.com/r/infp/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 320 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit infp \
--submission_flairs "Discussion" "Mental Health" "Informative" "Venting" "Advice" "Random Thoughts" "MBTI/Typing" "Relationships"

# https://www.reddit.com/r/isfj/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 140 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit isfj \
--submission_flairs "Discussion" "Question or Advice"

# https://www.reddit.com/r/ISTJ/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 130 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit ISTJ

# https://www.reddit.com/r/entj/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 170 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit entj \
--submission_flairs "Career" "Discussion" "Poll" "Functions" "Dating|Relationships" "Appreciation Post"

# https://www.reddit.com/r/enfj/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 140 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit enfj \
--submission_flairs "Advice" "Question" "Wholesome"

# https://www.reddit.com/r/ESFP/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 200 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit ESFP \
--submission_flairs "ESFP" "Other" "Question" "Advice" "Relationships"

# https://www.reddit.com/r/estp/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 300 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit estp \
--submission_flairs "ESTP Responses Only" "General Discussion" "Type Comparison Discussion" "Ask An ESTP"

# https://www.reddit.com/r/entp/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 190 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit entp \
--submission_flairs "Debate/Discussion" "Typology Help" "Advice" "Question/Poll" "MBTI Trends"

# https://www.reddit.com/r/ENFP/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 150 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit ENFP

# https://www.reddit.com/r/ESFJ/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 250 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit ESFJ \
--submission_flairs "Relationships" "Advice / Support" "Discussion / Poll"

# https://www.reddit.com/r/ESTJ/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 200 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit ESTJ \
--submission_flairs "Discussion/Poll" "Question/Advice" "Relationships"

# https://www.reddit.com/r/MBTIDating/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 400 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit MBTIDating \
--submission_flairs "all types welcome" "looking for ENFP" "looking for INFJ" "looking for ENTJ" "looking for ENTP"

# https://www.reddit.com/r/mbti/
python mbti_type_from_text/cli/fetch_hot_comments.py \
--db_path ${DB_PATH} \
--n_hot 560 \
--reddit_client_id ${REDDIT_CLIENT_ID} \
--reddit_client_secret ${REDDIT_CLIENT_SECRET} \
--subreddit mbti \
--submission_flairs "Theory Question" "Survey/Poll" "Stereotypes"
