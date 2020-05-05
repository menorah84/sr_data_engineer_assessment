
# Initial Solution Design

My main motivation was to use a single Cloud provider that will have all the required services. I also preferred serverless design for simplicity, although I am quite aware that a system that ingests both batch data (which can be fairly large than what we have here in the example) and streaming/real-time/near real-time data can be more complex and has far more components than what I have designed.

At the beginning, I decided to use AWS to implement the solution. I chose DynamoDB as the datastore to accommodate the required eventual flexibility in schema.

![AWS Solution Diagram](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/aws_solutions_diagram.png)

However, I hit a roadblock at DynamoDB, as QuickInsight **CANNOT** access data directly from DynamoDB yet. If I decided to do a workaround, this will complicate my solution and lengthen my development time, so I decided to switch to Google Cloud Platform as I am aware that Google Data Studio can directly interface with Google BigQuery. As BigQuery is more of a Data Warehouse solution, I designed the schema ahead to include the requirements in Assignment 2.

![GCP Solution Diagram](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_solutions_diagram.png)

# Implementation

The solution goes well for BigQuery especially the Assignment 1 part.

![GCP Cloud Functions](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_cloud_functions.png)

When it comes to Assignment 2, however, I was able to process streaming data but I discovered that Data Studio [CANNOT process GEOGRAPHY data type](https://cloud.google.com/bigquery/docs/gis-visualize) yet from BigQuery, so that part of the requirement was not satisfied. The Retail data generator uses *faker* library to generate some dummy.

![Online Retail Generator](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_online_retail_generator.png)

![GCP BigQuery](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_bigquery.png)

# How to Use

For the Assignment 1 part, the assumption is that it is a batch processing component. So the CSV file (or generically, some large data file) is stored in Cloud Storage bucket, which we call a landing zone, and the pipeline's REST API is invoked to commence processing to insert it into our data store (BigQuery).

![GCP Cloud Storage](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_cloud_storage.png)

![Postman Assignment 1](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/postman_assignment_1_call.png)

After processing, the pipeline moves that file to some other bucket (we use bucket "folder" in this example) to indicate that the pipeline is done with this.

![GCP Cloud Storage Processed](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/gcp_cloud_storage_processed.png)

For the Assignment 2 part, we send essentially the same payload, but instead of providing a Cloud Storage bucket/path where the data is, we include the data as part of the json.

![Postman Assignment 2](https://github.com/menorah84/sr_data_engineer_assessment/blob/master/img/postman_assignment_2_call.png)

We call the same REST API endpoint for the Cloud Function.

https://us-central1-fl-uw-03.cloudfunctions.net/online-retail

You can view the payloads in the [json_examples](https://github.com/menorah84/sr_data_engineer_assessment/tree/master/json_examples) folder.

(Note: While the Cloud Function REST endpoint is exposed publicly, it is not guaranteed to work for Assignment 1, as we should specify the files to be processed in the bucket. If there is no file there of such name, this will not work.) 

# Assignment 3: Improvements

So here are my ideas for improvement:
1. We could have used a schemaless datastore that has connector to some more powerful BI tool (that can also display geolocation data), say MongoDB and Tableau.
2. For the ETL pipeline, serverless approach (Lambda / Cloud Functions) obviously has its limitations, as it is actually designed for small routines / microservices rather than  throughput intensive tasks like data processing. We could have used more robust, more capable pipeline: Airflow, Amazon Elastic MapReduce, Amazon Glue, Google Cloud Dataflow, etc. Or if cost comes to mind, maybe we can use Amazon S3-Athena (Presto) so we can directly query S3 files. If streaming capability is a requirement, we may need to engineer pipelines that involves queue (Kafka, Pubsub, Kinesis, etc.)
3. Since this is retail data, there could be a time where a real-time analytics is necessary. In such a case, we may need other BI tools that can do exactly that (or even custom built dashboards using D3.js for example).
4. For Assignment 1, we are manually triggering the pipeline to commence processing of batch files. We can improve this by having the pipeline automatically trigger the process whenever it detects that a file is in the "landing" bucket.

# Front-end (visualization)

The final output can be seen here:

https://datastudio.google.com/reporting/15277472-df79-41e1-8b1f-0a43be99fff3
