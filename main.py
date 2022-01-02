from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
import flask

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index-video.html')


@app.route('/signup', methods=['GET'])
def signup():
    print("inside signup")
    return render_template('signup.html')


@app.route('/login', methods=['GET'])
def login():
    print("inside login")
    return render_template('login.html')


@app.route('/profile_home')
def profile_home():
    print("inside profile_home")
    api_object = CrudAPI()
    data=api_object.read()
    print("==data==", data)
    return render_template('profile_home.html', data=data)


@app.route('/add_new_password_page')
def add_new_password_page():
    return render_template('add_new_password.html')


@app.route('/login_validation', methods=["POST"])
def login_validation():
    print("inside login_validation")
    email = request.form.get("email")
    master_key = request.form.get("master_key")
    print("email:", email, "master_key:", master_key)
    if(str(email) == "sadman.93.sakib@gmail.com" and str(master_key) == "1"):
        print("Login successfully!!! ")
        return redirect(url_for('profile_home'))
    else:
        print("Login failed!!! ")
        return redirect(url_for('login'))

@app.route('/store_password_db', methods=["POST"])
def store_password_db():
    title = request.form.get("title")
    email = request.form.get("email")
    password = request.form.get("password")
    description = request.form.get("description")
    if(title != None and email != None and password != None):
        data = {'title': title,
                'email': email,
                'password': password,
                'description': description}
        api_object = CrudAPI()
        api_object.insert_data(new_document=data)
        return redirect(url_for('profile_home'))

# MongoDB Model for ToDo CRUD Implementation
class CrudAPI:
    def __init__(self):
        try:
            self.client = MongoClient(
                "mongodb+srv://admin:admin@cluster0.you2d.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
            self.database = 'personal_password_manager_db'
            self.db = self.client[self.database]
            self.collection = 'passwords'
        except:
            print("Unable to connect to database!")

    def insert_data(self, new_document):    # Create - (1) explained in next section
        response = self.db[self.collection].insert_one(new_document)
        output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output

    def read(self):                 # Read - (2) explained in next section
        documents = self.db[self.collection].find()
        output = [{item: data[item] for item in data}
                  for data in documents]
        return output

    def update_data(self):          # Update - (3) explained in next section
        filter = self.data['Filter']
        updated_data = {"$set": self.data['DataToBeUpdated']}
        response = self.collection.update_one(filter, updated_data)
        output = {'Status': 'Successfully Updated' if response.modified_count >
                  0 else "Nothing was updated."}
        return output

    def delete_data(self, data):    # Delete - (4) explained in next section
        filter = data['Filter']
        response = self.collection.delete_one(filter)
        output = {'Status': 'Successfully Deleted' if response.deleted_count >
                  0 else "Document not found."}
        return output


if __name__ == '__main__':
    app.run(debug=True)
