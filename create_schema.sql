CREATE DATABASE twitter_sentiment;
\c twitter_sentiment
CREATE TABLE tweets_by_topic (id serial, topic varchar(64), kafka_offset int, user_id varchar(64), tweet varchar(255), sentiment int, PRIMARY KEY (id))
