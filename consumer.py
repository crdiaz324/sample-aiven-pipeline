#!/usr/bin/env python
#  The following file uses a lot of code snippets from the Aiven getting started
#  documentation as well as the kafka-examples github repo.

from kafka import KafkaConsumer
import aiven_lib
from psycopg2.extras import RealDictCursor
import json, logging, sys, psycopg2


# Change the logging level in the line below to one of: 
# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

if __name__ == '__main__':
  
  # Read arguments and configurations and initialize
  args = aiven_lib.parse_args()
  config_file = args.config_file
  topic = args.topic
  conf = aiven_lib.read_config(config_file)

  # Configure the consumer  
  consumer = KafkaConsumer(
     args.topic,
     auto_offset_reset="earliest",
     client_id="aiven-client",
     group_id="group2",
     bootstrap_servers=conf['bootstrap.servers'],
     sasl_mechanism=conf['sasl.mechanisms'],
     sasl_plain_username=conf['sasl.username'],
     sasl_plain_password=conf['sasl.password'],
     security_protocol=conf['security.protocol'],
     ssl_cafile=conf['ssl_cafile'],
  )

  # Establish connection to Postgres
  conn = psycopg2.connect(conf['pg_uri'])
  cursor = conn.cursor(cursor_factory=RealDictCursor)

  insert_query = """
  INSERT INTO tweets_by_topic 
  (topic, kafka_offset, user_id, tweet, sentiment)
  values ( %s, %s, %s, %s, %s)
  """  

  try:
    count = 0
    while True:
      for _ in range(2):
        raw_msgs = consumer.poll(1.0)
        for tp, msgs in raw_msgs.items():
          for msg in msgs:            
              topic = msg.topic
              offset = msg.offset
              tweetdata = json.loads(msg.value)
              tweet = tweetdata['tweet']
              id_str = tweetdata['id_str']
              sentiment = tweetdata['sentiment']
              count += 1
              try:
                logging.debug(insert_query)
                cursor.execute(insert_query, (topic, offset, id_str, tweet, sentiment))
              except (Exception, psycopg2.Error) as error:
                if(conn): 
                  logging.error("Failed to insert record", error)
              conn.commit()  
              logging.debug("offset: {}\ntopic: {}\tid_str: {}\ntweet: {}\nsentiment: {}\n\n\n"
                    .format(offset, topic, id_str, tweet, sentiment))
  except KeyboardInterrupt:
    pass
  finally:
    if(conn):
        cursor.close()
        conn.close()
    # Leave group and commit final offsets
    consumer.close()  

