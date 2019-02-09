import redis
import json
from flask import Flask , request
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import ast
import pickle
import os.path
import collections
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
from time import strftime, gmtime

log_file = "app/log/app-{}.log".format(strftime("%b-%d-%Y-%H-%M-%S", gmtime()))
cred_file = "app/cred/token.pickle"
sys.stdout = sys.stderr = open(log_file,'wt')

app = Flask(__name__)

#Schema for validation 

dish_schema= {
         "type" : "object",
         "properties" : {
               "dish" : {"type": "string"},
               "ingredients" : {"type": "array"}
             },
        }

date_schema = {
	"type" : "object",
	"properties" : {
	      "dish" : {"type": "string"},
	      "date" : {"type": "string"} 

	     },
	
	}

TimeTuple = collections.namedtuple("TimedTuple", "start end")

#Method for obtaining redis client
def get_redis_client():
    HOSTNAME = "192.168.1.76" 
    PORT = 6379
    DB = 1

    return redis.StrictRedis(host=HOSTNAME, port = PORT, db = DB)

def uniq(client,dish):
    if len(client.lrange(dish,0,-1)) == 0:
        return True

    return False


#Scan redis using the provided cursor and count
def do_scan(client, cursor, count):
    status = {}

    if count <= 0:
        count = 10

    cursor, data = client.scan(cursor=cursor,count=count)


    if cursor == None or data == None:
        status['status']='Fail'
        status['error']='Scan cursor error or no keys returned'
        return status, 412

    status['status'] = 'Success'
    status['cursor'] = cursor
    status['data'] = data

    return status, 200

#gets the value of the key
def do_get(client,key):
    status = {}

    data = client.lrange(key,0,-1)

    if data == None:
        status['status']='Fail'
        status['error']='Key not found'
        return status, 404
    
    status['status'] = 'Success'
    status['data']= data
    status['key']= key

    return status, 200

#sets value in client
#does a method check (POST = UPDATE, PUT = NEW)
def do_set(method,client,key,value):
    status = {}

    
    #Check Unique
    if (method == 'POST') and (not uniq(client,key)):
        status['status'] = 'Fail'
        status['error'] = 'Dish already exists'
        return status, 422

    for ingredient in value:
	client.lpush(str(key),str(ingredient))    

    status['status']='Success'
    status['dish']=key
    status['ingredients']=value


    return status, 200


#search the redis space for a given set of keywords
def do_search(client,search_key):
    status = {}
    count = 200
    search = "*{}*".format(str(search_key))

    print("Searching...")
    cursor, data = client.scan(match=search,count = count)

    status['status'] = 'success'
    status['dishes'] = data

    return status, 200

#delete all values from key contained in the value parameter. If the key is empty delete
def do_del(client,key,value):
    status = {}

    for each in value:
	print(key)
	client.lrem(str(key),1,str(each))

    
    if len(client.lrange(str(key),0,-1)) == 0:
	client.delete(str(key))
   	status['removed'] = true

    status['status'] = 'Success'
    status['ingredients'] = value;	
    
    return status, 200


def get_Calendar_Creds():
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(cred_file):
        with open(cred_file, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

#Set event in Calendar
#Event Details { date, summaru, description)
def do_create_calendar_event(date, summary, item_list):

    service = get_Calendar_Creds()
    timestamps = start_stop_time(date)
    calendarID = "d665pq4cgkp0hi55imkonoq344@group.calendar.google.com"
    event = {}
 
    #date format MM/DD/YYYY HH:MM [PM/AM]
 
    event['summary'] = summary
    event['description'] = ",".join(item_list)
    event['start'] = { 'dateTime': timestamps.start }
    event['end'] = { 'dateTime': timestamps.end }

    event = service.events().insert(calendarId=calendarID, body=event).execute()    

    return event, 200

def start_stop_time(datetime):

 	#print(datetime.split(" "))	
	date,time,tod = datetime.split(" ")
	mo,d,y = date.split("/")
	#print(time.split(":"))
	h,m = time.split(":")

        if(tod == "PM"):
		h = str(int(h) + 12)	

	one_hour_plus = str(int(h) + 1)

	return TimeTuple(start="{}-{}-{}T{}:{}:00-07:00".format(y,mo,d,h,m), end="{}-{}-{}T{}:{}:00-07:00".format(y,mo,d,one_hour_plus,m))

	
#Scan endpoint that takes a cursor and count, then delivers the key space within
#the count and cursor
@app.route('/api/v1/dishes/',methods=['GET'])
def scan():
    cursor=str(request.args.get('cursor'))
    count=request.args.get('count')

    if cursor == 'None':
        cursor = '0'

    if count == None:
        count = 10

    client = get_redis_client()
    data, resp_code = do_scan(client,cursor,count)

    return json.dumps(data), resp_code


#Action get value of a given key
@app.route('/api/v1/dishes/dish',methods=['GET'])
def get_dish():
    dish = request.args.get('dish')

    if dish == None:
        data = {'status':'Fail','error':'No dish provided'}
        return json.dumps(data), 400

    client = get_redis_client()
    data, resp_code  = do_get(client,dish)

    return json.dumps(data), resp_code

#Set value on a given key
@app.route('/api/v1/dishes/dish',methods=['POST','PUT','DELETE'])
def modify_dish():
    client = get_redis_client()

    if not request.is_json:
        status={'status':'Fail','error':'No json provided'}
        return json.dumps(status), 400

    try:
        validate(request.get_json(),dish_schema)
    except ValidationError:
        status={'status':'Fail','error':'Invalid Json Format'}
        return json.dumps(status), 400

    if(len(request.get_json()['ingredients'])==0):
	status={'status':'Fail','error':'No Ingredients provided for dish'}
	return json.dumps(status),400

    data = request.get_json()

    if request.method == 'DELETE':
    	data, resp_code = do_del(client,data['dish'],data['ingredients'])
    else:
    	data, resp_code = do_set(request.method,client,data['dish'],data['ingredients'])

    return json.dumps(data), resp_code


#TODO - GET a partial scan of Keyspace given a search partial match of the key
@app.route('/api/v1/dishes/search',methods=['GET'])
def search():

    search = request.args.get('query')

    if search == None:
        data = {'status':'fail','error':'No search parameter provided'}
        return json.dumps(data), 412

    client = get_redis_client()

    print("In search web handler")
    data, resp_code = do_search(client,search)

    return json.dumps(data), resp_code

@app.route('/api/v1/dishes/date',methods=['PUT'])
def date_add():
   
    client = get_redis_client()

    if not request.is_json:
        status={'status':'Fail','error':'No json provided'}
        return json.dumps(status), 400

    try:
	validate(request.get_json(),date_schema)
    except ValidationError:
	print(request.get_json())
        status={'status':'Fail','error':'Invalid Json Format'}
        return json.dumps(status), 400	    


    data = request.get_json()

    items, st_code = do_get(client,data['dish'])
 
    status, resp_code  = do_create_calendar_event(data['date'],data['dish'],items['data'])   

    return json.dumps(status), resp_code

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)

