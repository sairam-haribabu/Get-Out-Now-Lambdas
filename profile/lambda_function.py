import json
import boto3
from boto3.dynamodb.conditions import Key


def get_user_db_data(userName): 
    table = boto3.resource('dynamodb').Table('user-table')
    result=table.query(KeyConditionExpression=Key('username').eq(userName))
    return result


def get_event_db_data(eventId):
    table = boto3.resource('dynamodb').Table('events')
    result=table.query(KeyConditionExpression=Key('id').eq(eventId))
    return result
    
    
def get_friends(friends):
    result = []
    for friend in friends:
        friend_data = get_user_db_data(friend)
        print("Friend_Data",friend_data)
        if friend_data['Items']:
            friend_result = {
                'username': friend_data['Items'][0]['username'], 
                'name': friend_data['Items'][0]['data']['name'], 
                'photo': friend_data['Items'][0]['data']['photo']
            }
            result.append(friend_result)
    return result


def get_events(events):
    result = []
    for event in events:
        event_data = get_event_db_data(event)
        if event_data['Items']:
            event_result = {
                'eventid': event_data['Items'][0]['id'], 
                'name': event_data['Items'][0]['data']['name'], 
                'photo': event_data['Items'][0]['data']['image']['url']
            }
            result.append(event_result)
    return result
    
    
def lambda_handler(event, context):
    print("Profile Lambda!")
    print("event:",event)
    print(event['key'])

    userName=event['key']
    userData = get_user_db_data(userName)
    
    if userData["Count"]:
        print(userData["Items"][0]['data'])
        friends_data = []
        if userData["Items"][0]['data']['friends']:
            friends_data = get_friends(userData["Items"][0]['data']['friends'])
        events_data = []
        if userData["Items"][0]['data']['events']:
            events_data = get_events(userData["Items"][0]['data']['events'])
        return {
            'statusCode': 200,
            'body': {'user': userData["Items"][0]['data'], 'friends': friends_data, 'events': events_data}
        }
    
    else:
        return {
            'statusCode': 404,
            'body': "User Not Found"
        }
        
