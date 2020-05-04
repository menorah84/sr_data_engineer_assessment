import json
import pandas as pd
import boto3
from botocore.exceptions import ClientError
from s3fs.core import S3FileSystem
from urllib.parse import urlparse
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('online_retail')

def lambda_handler(event, context):

    if event['data-source'] == 'json-payload':
        success_put_count = 0
        for row in event['data']:
            row['UnitPrice'] = str(row['UnitPrice'])
            try:
                table.put_item(Item=cast_to_decimal(row))
                success_put_count += 1
            except ClientError as e:
                pass
        
        total_records = len(event['data'])
        if success_put_count > 0:
            message = f'Success: Inserted {success_put_count} of {total_records} records of json payload to DynamoDB'
        else:
            message = 'Fail: No records were inserted'
            
        return {
            'statusCode': 200,
            'body': message
        }

    elif event['data-source'] == 's3' and 's3-path' in event:    
        o = urlparse(event['s3-path'])
        bucket = o.netloc
        filepath = o.path.lstrip('/')

        s3 = S3FileSystem(anon=False)
        df = pd.read_csv(s3.open(event['s3-path'], mode='rb'), dtype={ 'InvoiceNo': str, 'UnitPrice': str}, converters={'CustomerID': lambda id: str(int(float(id)))})
        success_put_count = df.apply(insert_to_table, axis=1).sum()
        s3.cp(event['s3-path'], 's3://' + bucket + '/processed' + filepath[filepath.rfind('/'):])
        s3.rm(event['s3-path'])
        
        s3_path = event['s3-path']
        if success_put_count > 0:
            message = f'Success: Inserted {success_put_count} of {df.shape[0]} records of data from S3 path {s3_path} to DynamoDB'
        else:
            message = 'Fail: No records were inserted'
        
        return {
            'statusCode': 200,
            'body': message
        }

    else:
        return { 'statusCode': 200, 'body': 'Error: data not valid' }

def cast_to_decimal(item):
    item['UnitPrice'] = Decimal(item['UnitPrice'])
    return item


def insert_to_table(row):
    try:
        table.put_item(Item=cast_to_decimal(row.to_dict()))
        return 1
    except ClientError as e:
        return 0
