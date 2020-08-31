import unittest
import consumer
import psycopg2
import testing.postgresql
from sqlalchemy import create_engine
import subprocess

def init_postgres():
    postgresql = testing.postgresql.Postgresql()
    print("postgresql up and running at {}".format(postgresql.url()))
    return postgresql

def setup_static_fetch(postgresql):
    subprocess.check_output(['psql', postgresql.url(), '-q', '-f', 'create_schema.sql'])

postgresql = init_postgres()
setup_static_fetch(postgresql)

class TestConsumer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        consumer.conn = psycopg2.connect(postgresql.url().replace("test", "twitter_sentiment"))
        consumer.conn.set_isolation_level( \
                psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    @classmethod
    def tearDownClass(cls):
        if not consumer.conn.closed:
            consumer.conn.close()

    def get_app(self):
        return consumer
    
    def setUp(self):
        # use db connection from server to make trasactions are effective
        self.cur = consumer.conn.cursor()
        self.cur.execute("BEGIN;")
        super(TestConsumer, self).setUp()

    def tearDown(self):
        self.cur.execute("ROLLBACK;")
        self.cur.close()
        super(TestConsumer, self).tearDown()
    
    def test_insert_query(self):
        insert_query = """
            INSERT INTO tweets_by_topic 
            (topic, kafka_offset, user_id, tweet, sentiment)
            values ( %s, %s, %s, %s, %s)
        """  
        self.cur.execute(insert_query, ("Quotes", "500", "1234567890", "Someone's sitting in the shade today because someone planted a tree a long time ago.", 1))
        consumer.conn.commit()
        self.cur.execute('SELECT topic, kafka_offset, user_id, tweet, sentiment FROM tweets_by_topic')
        self.assertEqual(self.cur.fetchone(), ('Quotes', 500, "1234567890", "Someone's sitting in the shade today because someone planted a tree a long time ago.", 1))
    
        
if __name__ == "__main__":
    consumer.conn = postgresql.url()
    unittest.main()

