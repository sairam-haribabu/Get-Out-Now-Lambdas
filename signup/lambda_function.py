import json
import boto3
from boto3.dynamodb.conditions import Key


def save_user_information(username, name, bio, photo):
    table = boto3.resource('dynamodb', region_name='us-east-1').Table('user-table')
    data = {
        'username': username,
        'data': {
            'name': name,
            'bio': bio,
            'friends': [],
            'events': [],
            'photo': photo
        }
    }
    response = table.put_item(Item=data)


def lambda_handler(event, context):
    username = event['username']
    name = event['name']
    bio = event['bio']
    photo=event['photo']
    save_user_information(username, name, bio, photo)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        'body': json.dumps('Hello from Lambda!'),
        'event': json.dumps(event)
    }
