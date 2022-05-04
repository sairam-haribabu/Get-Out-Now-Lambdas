import json
import boto3
from boto3.dynamodb.conditions import Key
import requests
from requests.auth import HTTPBasicAuth
from collections import defaultdict
from datetime import datetime


def get_os_data(search_msg):
    OS_HOST = "https://search-events-olistiprnbjai5j6547ry3ixra.us-east-1.es.amazonaws.com/_search?pretty"
    OS_HTTP_USER = 'master'
    OS_HTTP_PWD = "Abcd_1234"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    if len(search_msg) == 0:
        q = {
            'match_all': {}
        }
    else:
        # search message for date needs to be in datetime form
        # therefore if message is in date, include date in list of matches, otherwise don't 
        try: 
            try:
                date_msg = datetime.strptime(search_msg, '%Y-%M-%d')
            except:
                date_msg = datetime.strptime(search_msg, '%Y/%M/%d')
            
            matches = [
                {
                    'match': {
                        'dates': date_msg
                    } 
                }   
            ]
        except:
            matches = [
                {
                    'match': {
                        'name': "*" + search_msg + "*"
                    }
                }, 
                {
                    'match': {
                        'categories': search_msg
                    }
                }, 
                {
                    'match': {
                        'locations': search_msg
                    }
                }
            ]
        
        q = {
            'bool': {
                'should': matches, 
                'minimum_should_match': 1
            }
        }
    
    query = {
        'size': 12, 
        'query': q
    }
    
    response = requests.request('GET', OS_HOST, data=json.dumps(query), auth=HTTPBasicAuth(OS_HTTP_USER, OS_HTTP_PWD), headers=headers)
    print(json.loads(response.text))
    events = json.loads(response.text)['hits']['hits']
    if len(search_msg) == 0:
        events_list = [{'id': e['_source']['eventID'], 'name': e['_source']['name'], 'image': e['_source']['image']} for e in events]    
        events = {'all': events_list}
    else:
        events = categorize_matched_events(events, search_msg)
    return events
    
    
def categorize_matched_events(events, search_msg):
    print("events: ");
    print(events);
    matched_events = defaultdict(lambda: list())
    for e in events:
        for k, v in e['_source'].items():
            if search_msg in v: # matched to this field
                item = {
                    'id': e['_source']['eventID'], 
                    'name': e['_source']['name'], 
                    'image': e['_source']['image']
                }
                matched_events[k].append(item)
    return matched_events
    

def get_user_dynamo(user_name):
    print("attempting to get username")
    table = boto3.resource('dynamodb').Table('user-table')
    data = table.query(KeyConditionExpression=Key('username').eq(user_name))
    print("data: ")
    print(data)
    if data['Items']:
        return [data['Items'][0]]
    return list()
    
    
def lambda_handler(event, context):
    # TODO implement
    # Getting search keyword from event['key']
    key = event['key'].lower()
    events = get_os_data(key)
    users = list()
    if key:
        users = get_user_dynamo(key)
    
    return {
        'statusCode': 200,
        'body': {'events': events, 'users': users}
    }
