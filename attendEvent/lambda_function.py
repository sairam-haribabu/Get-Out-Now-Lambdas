import json
import boto3
from boto3.dynamodb.conditions import Key

def add_to_dynamo(name, id):
    user_table = boto3.resource('dynamodb').Table('user-table')
    events_table = boto3.resource('dynamodb').Table('events')
    print(name)
    result=user_table.query(KeyConditionExpression=Key('username').eq(name))
    print(result)
    if id not in result["Items"][0]['data']["events"]:
        event = result["Items"][0]['data']['events'].append(id)
        result = user_table.update_item(
            Key={
                'username': name
            },
            AttributeUpdates={
                'data':{
                    'Value': result["Items"][0]['data']
                }
            },
            ReturnValues="UPDATED_NEW"
        )
        print(result)
    
    result=events_table.query(KeyConditionExpression=Key('id').eq(id))
    print(result)
    if name not in result["Items"][0]['data']["attendees"]:
        event = result["Items"][0]['data']['attendees'].append(name)
        print(result["Items"][0]["data"])
        result = events_table.update_item(
            Key={
                'id': id
            },
            AttributeUpdates={
                'data':{
                    'Value': result["Items"][0]['data']
                }
            },
            ReturnValues="UPDATED_NEW"
        )
        print(result)
    
    
def lambda_handler(event, context):

    id = event["id"]
    name = event["name"]
    add_to_dynamo(name, id)
    return {
        'statusCode': 200,
        'body': "Successfully updated dynamo"
    }
