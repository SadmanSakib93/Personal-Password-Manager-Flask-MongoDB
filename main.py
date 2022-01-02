from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
import flask
from flask_paginate import Pagination, get_page_args

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index-video.html')


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/profile_home')
def profile_home():
    current_page_num = request.args.get('page', 1, type=int)
    print("current_page_num:", current_page_num)
    rows_per_page=1
    api_object = CrudAPI()
    data={}
    data['documents'] = api_object.read_by_page(rows_per_page=rows_per_page, page_num=current_page_num)
    data['num_of_documents']=len(api_object.read())
    data['rows_per_page']=rows_per_page
    data['current_page_num']=current_page_num
    print("==data==", data)
    return render_template('profile_home.html', data=data)


@app.route('/add_new_password_page')
def add_new_password_page():
    return render_template('add_new_password.html')


@app.route('/login_validation', methods=["POST"])
def login_validation():
    email = request.form.get("email")
    master_key = request.form.get("master_key")
    print("email:", email, "master_key:", master_key)
    if(str(email) == "sadman.93.sakib@gmail.com" and str(master_key) == "1"):
        print("Login successfully!!! ")
        return redirect(url_for('profile_home', page=1))
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

    def insert_data(self, new_document):
        response = self.db[self.collection].insert_one(new_document)
        output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output

    def read(self):
        documents = self.db[self.collection].find()
        output = [{item: data[item] for item in data}
                  for data in documents]
        return output

    def read_by_page(self, rows_per_page, page_num=1):
        # Set the pagination configuration
        page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
        print("page, per_page, offset", page, per_page, offset)
        documents = list(self.db[self.collection].find())
        print("documents:", len(documents))
        
        # Calculate number of documents to skip
        skips = rows_per_page * (page_num - 1)
        # Skip and limit
        data = self.db[self.collection].find().skip(skips).limit(rows_per_page)
        return data

    def update_data(self):
        filter = self.data['Filter']
        updated_data = {"$set": self.data['DataToBeUpdated']}
        response = self.collection.update_one(filter, updated_data)
        output = {'Status': 'Successfully Updated' if response.modified_count >
                  0 else "Nothing was updated."}
        return output

    def delete_data(self, data):
        filter = data['Filter']
        response = self.collection.delete_one(filter)
        output = {'Status': 'Successfully Deleted' if response.deleted_count >
                  0 else "Document not found."}
        return output


if __name__ == '__main__':
    app.run(debug=True)
