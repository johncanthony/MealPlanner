import redis
import json
from flask import Flask

app = Flask(__name__)

#Redis Connection information


def get_redis_client():
    HOSTNAME = [HOST] 
    PORT = 6379
    DB = 1

    return redis.StrictRedis(host=HOSTNAME, port = PORT, db = DB)


#TODO - Action Get a partial Scan of the KeySpace given a cursor position

#do_scan(client : StrictRedis, cursor: string, count: int)
# Takes the given client and performs a scan against the redis instance
# then forms the response object
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
def go_get(client,key):
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

#Default scan endpoint using the default 0 cursor and a count of 10 objects
@app.route('/api/v1/dishes/scan/',methods=['GET'])
def scan_root():
    cursor = 0
    count = 10
    client = get_redis_client()
    data, status = do_scan(client,cursor,count)

    return json.dumps(data), status

#Scan endpoint that takes a cursor and count, then delivers the key space within
#the count and cursor
@app.route('/api/v1/dishes/scan/<string:cursor>/<int:count>',methods=['GET'])
def scan(cursor='0',count=10):
    client = get_redis_client()
    data, status = do_scan(client,cursor,count)

    return json.dumps(data), status

#TODO - Action get value of a given key
@app.route('/api/v1/dishes/dish/<string:dish>')
def get_dish(dish):
    client = get_redis_client()
    data, status = go_get(client,dish)

    return json.dumps(data), status

#TODO - Set value on a given key

#TODO - GET a partial scan of Keyspace given a search partial match of the key

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
