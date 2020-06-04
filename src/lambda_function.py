import os
import logging
from elasticsearch import Elasticsearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth

es_host = os.getenv('ELASTICSEARCH_URL')
es_index = os.getenv('ELASTICSEARCH_INDEX')
key_name = os.getenv('KEY_NAME')
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
session_token = os.getenv('AWS_SESSION_TOKEN')
region = os.getenv('AWS_REGION')

# Establish connection to ElasticSearch
auth = AWSRequestsAuth(aws_access_key=access_key,
                       aws_secret_access_key=secret_access_key,
                       aws_token=session_token,
                       aws_host=es_host,
                       aws_region=region,
                       aws_service='es')

es = Elasticsearch(host=es_host,
                   port=443,
                   use_ssl=True,
                   connection_class=RequestsHttpConnection,
                   http_auth=auth)

print(es.info())


def lambda_handler(event, context):
    """Lambda Function entrypoint handler

    :event: DynamoDB Stream event
    :context: Lambda context
    :returns: Number of records processed

    """
    processed = 0
    for record in event['Records']:
        ddb_record = record['dynamodb']
        key = str(ddb_record['Keys'][key_name]['S'])
        if record['eventName'] == 'REMOVE':
            print("Deleting record: " + key)
            res = es.delete(index=es_index, doc_type='event', id=key)
        else:
            image = ddb_record['NewImage']
            res = es.index(index=es_index, doc_type='event',
                           id=key, body=image)

            print(res)
        processed = processed + 1

    print('Successfully processed {} records'.format(processed))
    return processed
