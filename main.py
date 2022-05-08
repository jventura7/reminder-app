from unicodedata import name
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_pymongo import PyMongo
import bcrypt
import pika
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/accounts"

mongo = PyMongo(app)
users = mongo.db.users
guardian = mongo.db.guardians
@app.route("/", methods = ['POST', 'GET'])
def home():
    if request.method == "POST":
        login_user = users.find_one({"username": request.form["username"]})
        login_guardian = guardian.find_one({"username": request.form["username"]})
        if login_user or login_guardian:
            if login_user:
                login = login_user
            else:
                login = login_guardian
        if bcrypt.hashpw(request.form["password"].encode("utf-8"), login["password"]) == login["password"]:
                session["username"] = request.form["username"]
                return redirect(url_for("user", nameID=session["username"], relationshipType=login["relationship"]))
        return "Invalid username/password combination"
    return render_template("index.html")

@app.route("/<nameID>/<relationshipType>", methods=['GET', 'POST'])
def user(nameID, relationshipType):
    # Establish RabbitMQ Connection
    credentials = pika.PlainCredentials('admin', 'password')
    parameters = pika.ConnectionParameters('172.29.107.22',
                                            5672,
                                            '/',
                                            credentials)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    if relationshipType == "Dependant":
        if request.method == "POST":
            guardName = request.form["guard_name"]
            findGuardian = guardian.find_one({"username": guardName})
            findDependant = users.find_one({"username": nameID})
            if guardName in findDependant["Guardians"]:
                flash("Guardian already linked!")
            elif findGuardian:
                guardian.update_one({"username": guardName}, 
                                    {"$set": {"Dependants": findGuardian["Dependants"] + [nameID]}})
                users.update_one({"username": nameID},
                                 {"$set": {"Guardians": findDependant["Guardians"] + [guardName]}})    
                flash("Successfully added guardian!")
            else:
                flash("Guardian doesn't exist!")
        elif request.method == "GET":
            # Begin RabbitMQ Consume
            getQueue = channel.queue_declare(queue=nameID, passive=True)

            channel.queue_bind(exchange='FinalProject', 
                               queue=nameID, 
                               routing_key=nameID)
            queueData = []

            for message in channel.consume(queue=nameID, inactivity_timeout=1):
                if not message[2]:
                    break
                method, properties, body = message
                print(body)
                queueData.append(json.loads(body.decode('utf-8')))
            print(queueData)
                
        return render_template("dependant.html", username=nameID)
    else:
        findGuardian = guardian.find_one({"username": nameID})
        if request.method == "POST":
            dependant, title, time, description = request.form["dependants"], request.form["title"], parse(request.form["meeting-time"]), request.form["description"]
            payload = {'title': title, 'time': time, 'description': description}

            # Create new queue with dependant name
            channel.queue_declare(queue=dependant, durable=True)
            channel.queue_bind(queue=dependant, exchange='FinalProject', routing_key=dependant)

            # Send reminder to queue
            channel.basic_publish(exchange='FinalProject', routing_key=dependant, body=json.dumps(payload))
            
        return render_template("guardian.html", username=nameID, dList=findGuardian["Dependants"])

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if request.method == "POST":
        checkEmpty = not request.form["username"] or not request.form["last_name"] or not request.form["username"] or not request.form["email"] or not request.form["password"]
        if checkEmpty:
            return "Error: Submit all fields!"
        existingUserName = users.find_one({"username" : request.form["username"]})
        existingUserEmail = users.find_one({"email": request.form["email"]})
        existingGuardianName = guardian.find_one({"username" : request.form["username"]})
        existingGuardianEmail = guardian.find_one({"email": request.form["email"]})

        if not existingUserName and not existingUserEmail and not existingGuardianName and not existingGuardianEmail:
            hashpass = bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt())
            currInfo = {"firstname": request.form["first_name"], 
                        "lastname": request.form["last_name"], 
                        "username": request.form["username"], 
                        "email": request.form["email"], 
                        "password" : hashpass, 
                        "relationship" : request.form["relationship"]
                        }
            if request.form["relationship"] == "Guardian":
                currInfo["Dependants"] = []
                guardian.insert_one(currInfo)
            else:
                currInfo["Guardians"] = []
                users.insert_one(currInfo)
            session["username"] = request.form["username"]
            return redirect(url_for("user", nameID=session["username"], relationshipType=currInfo["relationship"]))
        return "email or username is already registered"
    return render_template("signup.html")

def parse(schedule):
    year, month, day = schedule[:4], schedule[5:7], schedule[8:10]
    hour, minute = schedule[11:13], schedule[14:]
    return f"{year}-{month}-{day} {hour}:{minute}"

if __name__ == "__main__":
    app.secret_key = "my_secret"
    app.run(debug=True)