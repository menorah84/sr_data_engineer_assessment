
# Initial Solution Design

My main motivation was to use a single Cloud provider that will have all the required services. I also preferred serverless design for simplicity, although I am quite aware that a system that ingests both batch data (which can be fairly large than what we have here in the example) and streaming/real-time/near real-time data can be more complex and has far more components than what I have designed.

At the beginning, I decided to use AWS to implement the solution. I chose DynamoDB as the datastore to accommodate the required eventual flexibility in schema.

![AWS Solution Diagram](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/aws_solutions_diagram.png)

However, I hit a roadblock at DynamoDB, as QuickInsight **CANNOT** access data directly from DynamoDB yet. If I decided to do a workaround, this will complicate my solution and lengthen my development time, so I decided to switch to Google Cloud Platform as I am aware that Google Data Studio can directly interface with Google BigQuery. As BigQuery is more of a Data Warehouse solution, I designed the schema ahead to include the requirements in Assignment 2.

![GCP Solution Diagram](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_solutions_diagram.png)

# Implementation

The solution goes well for BigQuery especially the Assignment 1 part.

![GCP Cloud Functions](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_cloud_functions.png)

When it comes to Assignment 2, however, I was able to process streaming data but I discovered that Data Studio CANNOT process yet GEOGRAPHY data type from BigQuery, so that part of the requirement was not satisfied. The Retail data generator uses *faker* library to generate some dummy.

![Online Retail Generator](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_online_retail_generator.png)

![GCP BigQuery](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_bigquery.png)

# Assignment 3: Improvements

So here are my ideas for improvement:
1. We could have used a schemaless datastore that has connector to some more powerful BI tool (that can also display geolocation data), say MongoDB and Tableau.
2. For the ETL pipeline, serverless approach (Lambda / Cloud Functions) obviously has its limitations, as it is actually designed for small routines / microservices rather than  throughput intensive tasks like data processing. We could have used more robust, more capable pipeline: Airflow, Amazon Elastic MapReduce, Amazon Glue, Google Cloud Dataflow, etc. Or if cost comes to mind, maybe we can use Amazon S3-Athena (Presto) so we can directly query S3 files. If streaming capability is a requirement, we may need to engineer pipelines that involves queue (Kafka, Pubsub, Kinesis, etc.)
3. Since this is retail data, there could be a time where a real-time analytics is necessary. In such a case, we may need other BI wtools that can do exactly that. 

# Front-end (visualization)

The final output can be seen here:

https://datastudio.google.com/reporting/15277472-df79-41e1-8b1f-0a43be99fff3
