import json, boto3, requests, re
from boto3.dynamodb.conditions import Key, Attr
from requests.auth import HTTPBasicAuth
from collections import defaultdict
from datetime import datetime


def get_query(matches, size):
    return {
        'size': size, 
        'query': {
            'bool': {
                'should': matches, 
                'minimum_should_match': 1
            }
        }
    }    


def query_events(query):
    OS_HOST = "https://search-events-olistiprnbjai5j6547ry3ixra.us-east-1.es.amazonaws.com/_search?pretty"
    OS_HTTP_USER = 'master'
    OS_HTTP_PWD = "Abcd_1234"
    headers = {'Content-Type': 'application/json'}
    
    response = requests.request('GET', OS_HOST, data=json.dumps(query), auth=HTTPBasicAuth(OS_HTTP_USER, OS_HTTP_PWD), headers=headers)
    res = json.loads(response.text)
    print(res)
    
    return res['hits']['hits'] if 'hits' in res and 'hits' in res['hits'] else []


def get_os_data(search_msg):
    if " + " in search_msg:
        events = list()
        msgs = search_msg.split(" + ")
        for msg in msgs:
            matches = [
                {
                    'match': {
                        'categories': msg
                    }
                }, 
                {
                    'match': {
                        'city': msg.replace(",", "")
                    }
                }, 
            ]
            
            print("msg: {}".format(msg))
            events.extend(query_events(get_query(matches, 90)))
            print("events: {}".format(events))
        
        events_list = [{'id': e['_source']['eventID'], 'name': e['_source']['name'], 'image': e['_source']['image']} for e in events]    
        events = {'all': events_list}
    else:
        matches = [
            {
                'match': {
                    'categories': search_msg
                }
            }, 
            {
                'match': {
                    'city': search_msg.replace(",", "")
                }
            }, 
        ]
        
        # search message for date needs to be in datetime form
        # therefore if message is in date, include date in list of matches, otherwise don't 
        try: 
            try:
                date_msg = datetime.strptime(search_msg.replace("/", "-"), '%Y-%M-%d')
            except:
                date_msg = datetime.strptime(search_msg.replace("/", "-"), '%Y/%M/%d')
            
            date_msg = search_msg.replace("/", "-")
            print("date_msg: ")
            print(type(date_msg))
            print(date_msg)
            matches = [
                {
                    'match': {
                        'dates': date_msg
                    } 
                }   
            ]
        except:
            matches.append(
                {
                    'match': {
                        'aliases': search_msg
                    }
                }    
            )
    
        events = query_events(get_query(matches, 9))
        events = categorize_matched_events(events, search_msg)
    print("RETURNING EVENTS")
    print(events)
    return events
    
    
def categorize_matched_events(events, search_msg):
    print("events: ");
    print(events);
    matched_events = defaultdict(lambda: list())
    for e in events:
        for k, v in e['_source'].items():
            city_split = [sm for sm in re.split(', ', search_msg) if sm in v]
            if (k == "dates" and search_msg.replace("/", "-") in v) or (k == "city" and len(city_split) > 0 and all(city_split)) or search_msg in v: # matched to this field
                item = {
                    'id': e['_source']['eventID'], 
                    'name': e['_source']['name'], 
                    'image': e['_source']['image']
                }
                if k == "aliases": 
                    k = "name"
                matched_events[k].append(item)
                break
    return matched_events
    

def get_user_dynamo(name):
    print("attempting to get username")
    table = boto3.resource('dynamodb').Table('user-table')
    # data = table.query(
    #     KeyConditionExpression=Key('username').eq(name)
    # )
    response = table.scan()
    data = response['Items']
    users = [d for d in data if name in d['data']['name']]
    return users
    
    
def lambda_handler(event, context):
    # TODO implement
    # Getting search keyword from event['key']
    key = event['key'].lower()
    print("Key:",key)
    print(len(key))
    events = get_os_data(key)
    users = list()
    if " + " not in key:
        users = get_user_dynamo(key)
        print("users",users)
    
    return {
        'statusCode': 200,
        'body': {'events': events, 'users': users}
    }
