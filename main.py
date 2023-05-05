from flask import Flask, render_template, request, session
from pymongo import MongoClient
from threading import Thread
from flask import redirect
from pymongo import *
from flask import *
from bson.objectid import ObjectId
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)

app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)


try:
  client = MongoClient("mongodb+srv://abhiabhi:abhipass@cluster0.e3vf3.mongodb.net/fullStackDatabase?retryWrites=true&w=majority")
  db = client["fullStackDatabase"]
  collection = db["fullStackCollection"]
  commandCollection=db["fullStackCollection"]
  userCollection=db["userCollection"]
  print("======CONNECTED TO MONGODB DATABASE SUCCESSFULLY=======")
  print("====THE COLLECTION NAMES ARE ======")
  collection_names = db.list_collection_names()
  # print each collection name
  for name in collection_names:
      print(name)

except:
  print("ERRORRR!")


def run():
    app.run(host='0.0.0.0', port=8080)


def kanmani_alive():
    t = Thread(target=run)
    t.start()



class User(UserMixin):
    def __init__(self, user_dict):
        self.id = str(user_dict['_id'])
        self.username = user_dict['username']
        self.password_hash = user_dict['password_hash']
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    user_dict = userCollection.find_one({'_id': ObjectId(user_id)})
    if user_dict:
        return User(user_dict)
    return None


@login_manager.user_loader
def load_user(user_id):
    user_dict = userCollection.find_one({'_id': ObjectId(user_id)})
    if user_dict:
        return User(user_dict)
    return None


@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/resultscustom')
@login_required
def resultscustom():
  return render_template('resultscustom.html')


@app.route('/customjobs', methods=['GET', 'POST'])
@login_required
def customjobs():
  if request.method== 'POST':
    exp=request.form['exp']
    loc=request.form.get('loc')
    jobs=list(collection.find({'location':loc, 'experience':{'$lte': exp}}))
    print(jobs)
    return render_template('resultscustom.html', jobs=jobs, username=session['username'])
  unique_locations =collection.distinct('location')
  print("The unique locations are -")
  print(unique_locations)
  return render_template('customjobs.html', username=session['username'], unique_locations=unique_locations)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/show_jobs')
def show_jobs():
  jobs=list(collection.find())
  username = session.get('username',None)
  return render_template('home.html', jobs=jobs, username=username)

@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    if request.method == 'POST':
        print("A POST REQUEST HAS BEEN RECEIVED!!")
        print("=====A POST REQUEST HAS BEEN RECEIVED====")
        title = request.form['title']
        company = request.form['company']
        location = request.form['location']
        experience = request.form['experience']
        description = request.form['description']
        added_by = session['username']
        collection.insert_one({'title': title, 'company': company, 'location': location, 'experience' : experience, 'description': description, 'added_by':added_by})
        return redirect('/show_jobs')
    return render_template('add_job.html', username=session['username'])


@app.route('/delete_job/<job_id>')
@login_required
def delete_job(job_id):
    collection.delete_one({'_id': ObjectId(job_id)})
    return redirect('/show_jobs')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_dict = userCollection.find_one({'username': username})
        if user_dict and User(user_dict).check_password(password):
            user = User(user_dict)
            login_user(user)
            session['username']=username
            return redirect('/show_jobs')
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        userCollection.insert_one({'username': username, 'password_hash': password_hash})
        return redirect('/login')
    return render_template('register.html')

kanmani_alive()
app.run(debug=True)
