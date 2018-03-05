import redis
import json
from flask import Flask , request
from jsonschema import validate
from jsonschema.exceptions import ValidationError

app = Flask(__name__)

#Schema for validation 

schema= {
         "type" : "object",
         "properties" : {
               "dish" : {"type": "string"},
               "ingredients" : {"type": "array"}
             },
        }

#Method for obtaining redis client
def get_redis_client():
    HOSTNAME = "redis.home" 
    PORT = 6379
    DB = 1

    return redis.StrictRedis(host=HOSTNAME, port = PORT, db = DB)

def uniq(client,dish):
    if client.get(dish) == None:
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

    data = client.get(key)

    if data == None:
        status['status']='Fail'
        status['error']='Key not found'
        return status, 404
    
    status['status'] = 'Success'
    status['data']= data
    status['key']= key

    return status, 200

#sets value in client
def do_set(client,key,value):
    status = {}

    
    #Check Unique
    if not uniq(client,key):
        status['status'] = 'Fail'
        status['error'] = 'Dish already exists'
        return status, 422

    client.set(key,value)

    status['status']='Success'
    status['dish']=key
    status['ingredients']=value

    #update status and return

    return status, 200

#search the redis space for a given set of keywords
def do_search(client,search_key):
    status = {}
    count = 200
    search = "*{}*".format(str(search_key))

    cursor, data = client.scan(match=search,count = count)

    status['status'] = 'success'
    status['dishes'] = data

    return status, 200


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
@app.route('/api/v1/dishes/dish/',methods=['GET'])
def get_dish():
    dish = request.args.get('dish')

    if dish == None:
        data = {'status':'Fail','error':'No dish provided'}
        return json.dumps(data), 400

    client = get_redis_client()
    data, resp_code  = do_get(client,dish)

    return json.dumps(data), resp_code

#Set value on a given key
@app.route('/api/v1/dishes/dish',methods=['POST'])
def set_dish():
    client = get_redis_client()

    if not request.is_json:
        status={'status':'Fail','error':'No json provided'}
        return json.dumps(status), 400

    try:
        validate(request.get_json(),schema)
    except ValidationError:
        status={'status':'Fail','error':'Invalid Json Format'}
        return json.dumps(status), 400

    data = request.get_json()

    data, resp_code = do_set(client,data['dish'],data['ingredients'])

    return json.dumps(data), resp_code


#TODO - GET a partial scan of Keyspace given a search partial match of the key
@app.route('/api/v1/dishes/search',methods=['GET'])
def search():

    search = request.args.get('query')

    if search == None:
        data = {'status':'fail','error':'No search parameter provided'}
        return json.dumps(data), 412

    client = get_redis_client()

    data, resp_code = do_search(client,search)

    return json.dumps(data), resp_code


if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
def uniq(redis,dish):
    if redis.get(dish) ==  None:
        return True

    return False
