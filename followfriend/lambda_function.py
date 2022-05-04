import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    # TODO implement
    print(event)
    username=event['username']
    friendName=event['friendname']
    
    print(event)
    
    table = boto3.resource('dynamodb').Table('user-table')
    result=table.query(KeyConditionExpression=Key('username').eq(username))
    print(result)
    result["Items"][0]['data']['friends'].append(friendName)

    result = table.update_item(
        Key={
            'username': username
        },
        AttributeUpdates={
            'data':{
                'Value': result["Items"][0]['data']
            }
        },
        ReturnValues="UPDATED_NEW"
    )
    
    print("Result:",result)
    return {
        'statusCode': 200,
        'body': result
    }
