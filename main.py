from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
db = PyMongo(app).db
app.secret_key = "key"
app.permanent_session_lifetime = timedelta(minutes=10)

# class users(db.Model):
    # _id = db.Column("id", db.Inteder, primary_key=True)
    # name = db.Column(db.String(100))
    # email = db.Column(db.String(100))

    # def __init__(self, name, email):
    #     self.name = name
    #     self.email = email

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user

        """
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, "")
            db.session.add(usr)
            db.commit()
        """

        flash(f"Successfully logged in!", "info")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash(f"Already logged in!", "info")
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST" and request.form["username"]:
        session.pemanent = True
        user = request.form["username"]
        session["user"] = user
        flash(f"Successfully created account!", "info")
        return redirect(url_for("user"))
    else:
        return render_template("signup.html")


@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            # found_user = users.query.filter_by(name=user).first()
            # found_user.email = email 
            # db.commit()
            flash(f"Successful email!", "info")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    flash(f"Logout successful", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)
