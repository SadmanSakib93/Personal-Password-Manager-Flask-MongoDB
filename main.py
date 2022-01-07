from flask import Flask, flash, render_template, redirect, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from cryptography.fernet import Fernet
import math

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
private_key = b'arDX139818LacYNQ78TCm8D6iOm1HrvRnvOCKMlebj8='

@app.route("/")
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/profile_home')
def profile_home():
    current_page_num = request.args.get('page', 1, type=int)
    rows_per_page = 5
    api_object = CrudAPI()
    data = {}
    data['documents'] = list(api_object.read_by_page(
        rows_per_page=rows_per_page, page_num=current_page_num))
    data['num_of_documents'] = len(api_object.read())
    data['curr_page_num_of_documents'] = len(data['documents'])
    data['rows_per_page'] = rows_per_page
    data['current_page_num'] = current_page_num
    data['total_num_of_pages'] = math.ceil(
        data['num_of_documents']/data['rows_per_page'])
    
    fernet = Fernet(private_key)
    for doc_index in range(len(data['documents'])):
        data['documents'][doc_index]['password'] = fernet.decrypt(data['documents'][doc_index]['password']).decode()
    return render_template('profile_home.html', data=data)


@app.route('/add_new_password_page')
def add_new_password_page():
    return render_template('add_new_password.html')


@app.route('/update_item')
def update_item():
    id = request.args.get('id', 1, type=str)
    api_object = CrudAPI()
    data = {}
    data['documents'] = api_object.read_by_document_id(id)
    fernet = Fernet(private_key)
    data['documents']['password'] = fernet.decrypt(data['documents']['password']).decode()
    return render_template('update_item.html', data=data)


@app.route('/login_validation', methods=["POST"])
def login_validation():
    email = request.form.get("email")
    master_key = request.form.get("master_key")
    if(str(email) == "ppm@ppm.com" and str(master_key) == "ppm_admin"):
        print("Login successfully!!! ")
        return redirect(url_for('profile_home', page=1))
    else:
        print("Login failed!!! ")
        flash("Login failed. Wrong email or master key!")
        return redirect(url_for('login'))


@app.route('/store_password_db', methods=["POST"])
def store_password_db():
    title = request.form.get("title")
    email = request.form.get("email")
    password = request.form.get("password")
    description = request.form.get("description")
    fernet = Fernet(private_key)
    password_encrypted = fernet.encrypt(password.encode())
    if(title != None and email != None and password_encrypted != None):
        data = {'title': title,
                'email': email,
                'password': password_encrypted,
                'description': description}
        api_object = CrudAPI()
        api_object.insert_data(new_document=data)
        return redirect(url_for('profile_home'))


@app.route('/update_password_db', methods=["POST"])
def update_password_db():
    title = request.form.get("title")
    email = request.form.get("email")
    password = request.form.get("password")
    description = request.form.get("description")
    update_id = request.form.get("update_id")
    fernet = Fernet(private_key)
    password_encrypted = fernet.encrypt(password.encode())
    if(title != None and email != None and password_encrypted != None):
        data = {'title': title,
                'email': email,
                'password': password_encrypted,
                'description': description}
        api_object = CrudAPI()
        response = api_object.update_data_by_id(
            update_data=data, update_id=update_id)
    return redirect(url_for('profile_home'))


@app.route('/delete_document_db', methods=["POST"])
def delete_document_db():
    id_document = str(request.get_data())
    api_object = CrudAPI()
    try:
        response = api_object.delete_data(
            ObjectId(id_document[2:len(id_document)-1]))
        return response
    except:
        print("Unable to delete!")
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

    def read_by_document_id(self, id):
        documents = self.db[self.collection].find_one({'_id': ObjectId(id)})
        return documents

    def read_by_page(self, rows_per_page, page_num=1):
        # Calculate number of documents to skip
        skips = rows_per_page * (page_num - 1)
        # Skip and limit
        data = self.db[self.collection].find().skip(skips).limit(rows_per_page)
        return data

    def update_data_by_id(self, update_data, update_id):
        filter = ObjectId(update_id)
        response = self.db[self.collection].update_one(
            {"_id": filter}, {"$set": update_data})
        output = {'Status': 'Successfully Updated' if response.modified_count >
                  0 else "Nothing was updated."}
        return output

    def delete_data(self, id_document):
        response = self.db[self.collection].delete_one({"_id": id_document})
        output = {'message': 'Successfully Deleted' if response.deleted_count >
                  0 else "Record not found."}
        return output


if __name__ == '__main__':
    app.run(debug=True)
