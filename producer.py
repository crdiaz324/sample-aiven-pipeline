#!/usr/bin/env python

from kafka import KafkaProducer
import aiven_lib
import os, logging, sys, json, time
import tweepy as tw
# import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode

# Change the logging level in the line below to one of: 
# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

if __name__ == '__main__':
  
  # Read arguments and configurations and initialize
  args = aiven_lib.parse_args()
  config_file = args.config_file
  topic = args.topic
  conf = aiven_lib.read_config(config_file)
  
  # Configure the producer
  producer = KafkaProducer(
     bootstrap_servers=conf['bootstrap.servers'],
     sasl_mechanism=conf['sasl.mechanisms'],
     sasl_plain_username=conf['sasl.username'],
     sasl_plain_password=conf['sasl.password'],
     security_protocol=conf['security.protocol'],
     ssl_cafile=conf['ssl_cafile']
  )
  
  # Twitter connection settings
  consumer_key=conf['consumer_key']
  consumer_secret=conf['consumer_secret']
  access_token=conf['access_token']
  access_token_secret=conf['access_token_secret']

  # Establish tweepy connection
  auth = tw.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

  # Set up the sentiment analyzer 
  analyzer = SentimentIntensityAnalyzer()
  
  # Override tweepy.StreamListener add add on_data logic
  class MyStreamListener(tw.StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            if len(data) > 1:
                # Get the tweet text
                tweet = 'unknown'
                try:
                    if None != data['text']:
                        tweet = data['text']
                    elif None != data['full_text']:
                        tweet = data['full_text']
                    
                except KeyError as e:
                    logging.error("Error on_data %s" % str(e))
                tweet.encode('utf-8')

                # Timestamp of the tweet
                time_ms = 'unknown'
                try:
                    if None != data['timestamp_ms']:
                        time_ms = data['timestamp_ms']

                except KeyError as e:
                    logging.error("Error on_data %s" % str(e))
                
                # Id of the user that composed this tweet
                id_str = 'unknown'
                try:
                    if None != data['id_str']:
                        id_str = data['id_str']

                except KeyError as e:
                    logging.error("Error on_data %s" % str(e))
                
                # Determine the sentiment of the tweet
                vs = analyzer.polarity_scores(tweet)
                sentiment = vs['compound']
                if not tweet.startswith('RT'):
                    message = json.dumps({"time_ms": time_ms, "id_str": id_str, "tweet": tweet, "sentiment": sentiment}, sort_keys=True)
                    logging.debug(message)
                    producer.send(topic, message.encode("utf-8"))
                return True

        except BaseException as e:
            logging.error("Error on_data %s" % str(e))
            return true

  myStreamListener = MyStreamListener()
  myStream = tw.Stream(auth = api.auth, listener=myStreamListener, tweet_mode='extended')
  myStream.filter(track=[topic], is_async=True)

