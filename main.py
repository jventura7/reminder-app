from unicodedata import name
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_pymongo import PyMongo
import bcrypt
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
        return render_template("dependant.html", username=nameID)
    else:
        findGuardian = guardian.find_one({"username": nameID})
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

if __name__ == "__main__":
    # db.create_all()
    app.secret_key = "my_secret"
    app.run(debug=True)