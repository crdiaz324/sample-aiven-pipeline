# sample-aiven-pipeline

This project is a sample data pipline built on the Aiven.io infrastructure. This pipeline will follow a twitter topic (mention) and stream that data into a Kafka topic.  Then a consumer will read from that topic and push the data to a Postgres backend.  The infrastructure for both Kafka and Postgres were created with a with a few clicks on the Aiven.io Console.  

To run this project on your own environment simply follow the directions in the Quickstart section.

## Quickstart 

