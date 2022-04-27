import json
import boto3
from boto3.dynamodb.conditions import Key


def get_db_data(userName): 
    table = boto3.resource('dynamodb').Table('user-table')
    result=table.query(KeyConditionExpression=Key('username').eq(userName))
    return result

def lambda_handler(event, context):
    print("Profile Lambda!")
    print(event['username'])

    userName=event['username']
    userData = get_db_data(userName)
    if userData["Count"]:
        print(userData["Items"][0]['data'])
    
        return {
            'statusCode': 200,
            'body': userData["Items"][0]['data']
        }
    else:
         return {
            'statusCode': 404,
            'body': "User Not Found"
        }
        
