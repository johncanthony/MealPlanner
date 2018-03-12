import redis
import yaml

redis_server = '192.168.1.76'
port = 6379
db=1
data_file= 'dishes.json'



def load_dishes():
    
    with open(data_file,"r") as file:
        data = yaml.safe_load(file)
        dishes = data['dishes']

    return dishes

#for dish in dishes['dishes']:
#    summary = dish['summary']
#    if not counts.has_key(summary):
#        counts[summary]=1
#    else:
#        counts[summary]+=1

def uniq(redis,dish):
    if len(redis.lrange(dish,0,-1)) == 0 :
        return True

    return False

def valid(dish):

    if not dish.has_key('ingredients'):
        return False

    if not dish.has_key('summary'):
        return False

    return True

			

def main():

    client = redis.StrictRedis(host=redis_server, port=port,db=db)
    dishes = load_dishes()
    for dish in dishes:
        if valid(dish) and (uniq(client, dish['summary'])):
	    
	    for ing in dish['ingredients']:
		client.lpush(dish['summary'].strip(),ing.strip())	    
            #client.set(dish['summary'],dish['ingredients'])
            print(client.lrange(dish['summary'],0,-1))
	    
           

if __name__ == "__main__":
    main()

