#Author: Noah Sanzone

import pika
import json

# incomming message: username (routing key), title, message, time reminder is set for

def callback(ch, method, properties, body):
    getQueue.method.message_count -= 1
    print("%r:%r" % (method.routing_key, json.load(body)))
    #print("Message Count:", getQueue.method.message_count)
    if getQueue.method.message_count == 0:
        channel.stop_consuming()


dict1 = {"username": "user1",
         "title": "meds",
         "message": "take your meds",
         "time": "6:00"}

# dict2 = {"username": "user2",
#          "title": "walk",
#          "message": "go for a walk",
#          "time": "12:00"}
#
# dict3 = {"username": "user3",
#          "title": "work",
#          "message": "do your work",
#          "time": "18:00"}

# need to see if user already exists in the queue

# get the username
username = dict1.get("username")

raspIP = "172.29.107.22"

# Establish RabbitMQ connection
credentials = pika.PlainCredentials('admin', 'password')
parameters = pika.ConnectionParameters(raspIP,
                                           5672,
                                           '/',
                                           credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

action = "c"
warehouse = "FinalProject"
collection = username
dictionary = dict1

if action == "p":
    channel.basic_publish(exchange=warehouse,
                          routing_key=collection,
                          body=json.dumps(dictionary))
else:
    getQueue = channel.queue_declare(queue=collection,
                                     passive=True)

    channel.queue_bind(exchange=warehouse,
                       queue=collection,
                       routing_key=collection)

    channel.basic_consume(queue=collection,
                          on_message_callback=callback,
                          auto_ack=True)

    channel.start_consuming()




# guardian submits a post request
# dependent submit a get request








#
# connection = pika.BlockingConnection(parameters)
# channel = connection.channel()

# tutorial on youtube techwithtim for flask
# John's IP: 172.29.45.136

# make a file with reminders and get it working using a priority queue
# make a dictionary that acts as reminder

