import json, gcsfs
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
from decimal import Decimal

from google.cloud import bigquery
from google.cloud import storage

bq_client = bigquery.Client()

def online_retail(request):

    params = request.get_json()
    
    if not 'project' in params or not 'dataset' in params or not 'table' in params:
        return "Missing project, BigQuery dataset or table argument!"
        
    bq_table = params['project'] + '.' + params['dataset'] + '.' + params['table']
    
    try:
        bq_client.get_table(bq_table)
    except:
        # Most likely table is non-existent
        return "Error: Project, BigQuery dataset or table non-existent!"

    if params['data-source'] == 'json-payload':
        insert_response = bq_client.insert_rows_json(bq_table, params['data'])
        
        total_records = len(params['data'])
        total_inserted_records = total_records - len(insert_response)
        if total_inserted_records > 0:
            message = f'Success: Inserted {total_inserted_records} of {total_records} records of json payload to BigQuery'
        else:
            message = f'Fail: No records were inserted {json.dumps(insert_response)}'
            
        return message

    elif params['data-source'] == 'cloud-storage' and 'cloud-storage-path' in params:            
        df = pd.read_csv(   
                            params['cloud-storage-path'], 
                            dtype = { 'InvoiceNo': str, 'Quantity': int, 'UnitPrice': str, 'CustomerID': str }, 
                            converters = { 'InvoiceDate': date_converter }
                        )

        df['UnitPrice'] = df['UnitPrice'].map(Decimal)
        
        schema = [
            bigquery.schema.SchemaField('InvoiceNo', 'STRING', mode='REQUIRED'),
            bigquery.schema.SchemaField('StockCode', 'STRING', mode='REQUIRED'),
            bigquery.schema.SchemaField('Description', 'STRING', mode='NULLABLE'),
            bigquery.schema.SchemaField('Quantity', 'INTEGER', mode='NULLABLE'),
            bigquery.schema.SchemaField('InvoiceDate', 'STRING', mode='NULLABLE'),
            bigquery.schema.SchemaField('UnitPrice', 'NUMERIC', mode='NULLABLE'),
            bigquery.schema.SchemaField('CustomerID', 'STRING', mode='NULLABLE'),
            bigquery.schema.SchemaField('Country', 'STRING', mode='NULLABLE')
        ]
        
        load_job_config = bigquery.job.LoadJobConfig(schema=schema, encoding='UTF-8')
        
        load_job = bq_client.load_table_from_dataframe(df, bq_table, parquet_compression='gzip', job_config=load_job_config)
        
        # load_job = bq_client.load_table_from_dataframe(df, bq_table, parquet_compression='gzip')
        # insert_response = bq_client.insert_rows_json(bq_table, df.to_dict(orient='records'))

        cloud_storage_path = params['cloud-storage-path']
        o = urlparse(cloud_storage_path)
        bucket_name = o.netloc
        filepath = o.path.lstrip('/')

        # Move processed file
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(filepath)
        bucket.rename_blob(blob, 'processed' + filepath[filepath.rfind('/'):])
        
        """
        total_records = df.shape[0]
        total_inserted_records = total_records - len(insert_response)
        
        if total_inserted_records > 0:
            message = f'Success: Inserted {total_inserted_records} of {total_records} records of data from Cloud Storage {cloud_storage_path} to BigQuery'
        else:
            message = f'Fail: No records were inserted {json.dumps(insert_response)}'
        
        return message
        """
        
        return f'Created a load job with id {load_job.job_id} to insert data from Cloud Storage {cloud_storage_path} to BigQuery table'

    else:
        return 'Error: data not valid'


def date_converter(dt):
    return datetime.strptime(dt, "%m-%d-%Y %H:%M").strftime("%Y-%m-%d %H:%M:00.000")


"""
# Object of type Decimal is not JSON serializable
def decimal_converter(price):
    return Decimal(price)    
"""    
    