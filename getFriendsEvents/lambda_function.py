import json
import boto3
from boto3.dynamodb.conditions import Key


def get_user_friends(username): 
    table = boto3.resource('dynamodb').Table('user-table')
    user = table.query(KeyConditionExpression=Key('username').eq(username))
    friends = user["Items"][0]["data"]["friends"]
    return friends
    
def get_friends_events(friends):
    table = boto3.resource('dynamodb').Table('user-table')
    event_ids = list()
    for f in friends:
        friend = table.query(KeyConditionExpression=Key('username').eq(f))
        print("friend: ")
        print(friend)
        if len(friend["Items"]) > 0:
            event_ids.extend(friend["Items"][0]["data"]["eventsAttending"])
    print("event_ids")
    
def get_events(event_ids):
    events = list()
    if event_ids is None:
        table = boto3.resource('dynamodb').Table('events')
        for id in event_ids:
            response = table.query(KeyConditionExpression=Key('id').eq(id))
            events.append(response["Items"][0])
    return events

def lambda_handler(event, context):
    username = event['username']
    friends = get_user_friends(username)
    event_ids = get_friends_events(friends)
    events = get_events(event_ids)
    print("Events: ")
    print(events)
    # TODO implement
    return {
        'statusCode': 200,
        'body': events
    }
