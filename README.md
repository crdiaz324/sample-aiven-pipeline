# sample-aiven-pipeline

This project is a sample data pipeline built on the Aiven.io infrastructure. This pipeline will follow a twitter topic (mention), determine the sentiment of the tweet and stream that data into a Kafka topic.  Then a consumer will read from that topic and push the data to a Postgres backend.  The infrastructure for both Kafka and Postgres were created with a few clicks on the Aiven.io Console.  

To run this project on your own environment simply clone this repo and follow the directions in the sections below.

### Setup

To get started, you will first need to sign up for a free account on Aiven.io.  Once your account is created, setup a Kafka and a Postgres service.  

#### Kafka Service

For directions on setting up the Kafka service, follow their getting started documentation https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka.  Just follow the directions up to the point of getting your Kafka service up and running.  You will use the code in this repo produce and consume data to/from Kafka.

#### Postgres Service

We will setup the Postgres service next.  To get the Postgres service up and running, follow the Aiven's directions listed here https://help.aiven.io/en/articles/489573-getting-started-with-aiven-postgresql.  Here again we will just follow the direction up to the point that the service is up and running.  

After the service is running, we can run the create_schema.sql file to create the database and table.

#### Credentials file

After both of those services are up and running, the next step is to create a file to hold all your credentials.  This file should be stored outside of this repo to avoid accidently uploading your credentials to github.  The file should look something like this:

```
bootstrap.servers=<<Kafka service URI>>
security.protocol=SASL_SSL
sasl.mechanisms=PLAIN
sasl.username=<<Kafka user>>
sasl.password=<<Kafka password>>
ssl_cafile=<</path/to/your/ca.cert>>
consumer_key=<<Twitter API key>>
consumer_secret=<<Twitter API secret key>>
access_token=<<Twitter access token secret>>
access_token_secret=<<Twitter access toekn>>
pg_uri=<<Postgres Service URI>>
```

Everything except for the Twitter settings, can be found on the Aiven console.  For the Twitter settings, you will have to create an app here  https://developer.twitter.com/en/apps. After the app is created, copy your keys into this file.  

#### Activate your virtualenv and install all requirements

This code was tested with Python 3.6.8, for best results, it is recommended to create a virtualenv with the same Python version and install all the python modules there.  

In my environment, I run the following commands to activate the vritualenv and install all my requirements

```
$ virtualenv -p ~/.asdf/installs/python/3.6.8/bin/python aiven-venv
$ source aiven-venv/bin/activate
$ pip install -r requirements.txt
```

That's it!  Now we just need to create a topic on Kafka that matches the keyword or mention that you want to track on Twitter and run the application to capture all tweets related to your keyword, determine the sentiment of the tweet and store the results in Postgres.


### Running the producer

To run the producer, choose a keyword, in my case I chose two keywords, "trump" and "biden."  Since we are so close to the presidential elections, both of those keywords have a lot of activity so it’s easy to get some quick results.  I then created both of those topics on the Aiven console's Kafka topic tab.  

Next, I simply ran the following commands from within the repo:

```
$ ./producer.py -f ../aiven.config -t biden
$ ./producer.py -f ../aiven.config -t trump
```

Both of those commands will run until you manually stop them.  The -f flag specifies the path to the credentials file described above.  The -t flag has two purposes, it will serve as the keyword to track on Twitter as well as the topic to post the messages to.  

### Running the consumer

The consumer will read the data from the specified topic and insert it into your Postgres database that you setup above.  

To run the consumer, you will run consumer.py with the same options as the producer in the step above.

```
$ ./consumer.py -f ../aiven.config -t biden
$ ./consumer.py -f ../aiven.config -t trump
```

### End result

After running these jobs for about 15 minutes each, we can get a general idea of the overall sentiment for both candidates based on the tweets over that time period.  Here is an example of the output that was captured during my test run:

```
twitter_sentiment=> select topic, count(*) from tweets_by_topic group by topic;
 topic | count
-------+-------
 biden |  2160
 trump |  2039
(2 rows)

twitter_sentiment=> SELECT topic, AVG(sentiment) from tweets_by_topic group by topic;
 topic |         avg
-------+----------------------
 biden | -0.02276384223131808
 trump | -0.06734404055123176
(2 rows)

twitter_sentiment=>
```
