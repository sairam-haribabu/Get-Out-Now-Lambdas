import json
import boto3
from boto3.dynamodb.conditions import Key

    
def lambda_handler(event, context):
    # TODO implement
    key = event['key']
    print("K", key)
    
    table = boto3.resource('dynamodb').Table('events')
    result = table.query(KeyConditionExpression=Key('id').eq("Z7r9jZ1Ad8pJf"))
    print("R", result)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }