import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from flask import Flask, request, jsonify, render_template, redirect, flash, send_file, url_for, session
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.utils import secure_filename
import bcrypt
import joblib
import pickle
import matplotlib.pyplot as plt
import os

app = Flask(__name__) #Initialize the flask App
app.secret_key = "caircocoders-ednalan-2020"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tesslane'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

picFolder = os.path.join('static','pics')

app.config['UPLOAD_FOLDER'] = picFolder

@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",(name,email,hash_password,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return render_template("home.html")    

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template("upload.html")
            else:
               mesage = 'Incorrect Email or Password '
               return render_template('login.html', mesage = mesage)
        else:
            mesage = 'Incorrect Email or Password '
            return render_template('login.html', mesage = mesage)
    else:
        return render_template("login.html")


@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/preview',methods=["POST"])
def preview():
    if request.method == 'POST':
        dataset = request.files['datasetfile']
        df = pd.read_csv(dataset,encoding = 'unicode_escape')
        return render_template("preview.html",df_view = df)

@app.route('/predict',methods=['POST','GET'])
def predict():
    item_weight= float(request.form['item_weight'])
    item_fat_content=float(request.form['item_fat_content'])
    item_type= float(request.form['item_type'])
    item_mrp = float(request.form['item_mrp'])
    outlet_establishment_year= float(request.form['outlet_establishment_year'])
    outlet_size= float(request.form['outlet_size'])
    outlet_type= float(request.form['outlet_type'])

    X= np.array([[ item_weight,item_fat_content,item_type,item_mrp,
                  outlet_establishment_year,outlet_size,outlet_type ]])

    scaler_path= r'C:\Python3\Scripts\TessLane\model\sc.sav'
    sc=joblib.load(scaler_path)
    X_std= sc.transform(X)
    model_path=r'C:\Python3\Scripts\TessLane\model\xg.sav'
    model= joblib.load(model_path)
    Y_pred=model.predict(X_std)
   # return jsonify({'Prediction': float(Y_pred)})
    return render_template('result.html', prediction_text= float(Y_pred))


@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/chart')
def chart():
    ItemWeight = os.path.join(app.config['UPLOAD_FOLDER'], 'ItemWeight.jpg')
    ItemMRP = os.path.join(app.config['UPLOAD_FOLDER'], 'ItemMRP.jpg')
    ItemSales = os.path.join(app.config['UPLOAD_FOLDER'], 'ItemSales.jpg')
    OutletSize = os.path.join(app.config['UPLOAD_FOLDER'], 'OutletSize.jpg')
    IFC = os.path.join(app.config['UPLOAD_FOLDER'], 'IFC.jpg')
    ItemType = os.path.join(app.config['UPLOAD_FOLDER'], 'ItemType.jpg')
    OutletType = os.path.join(app.config['UPLOAD_FOLDER'], 'OutletType.jpg')
    OutletYear = os.path.join(app.config['UPLOAD_FOLDER'], 'OutletYear.jpg')
    return render_template("chart.html", user_image = ItemWeight, user_image2 = ItemMRP, user_image3 = ItemSales, user_image4 = OutletSize, user_image5 = IFC, user_image6 = ItemType, user_image7 = OutletType, user_image8 = OutletYear)

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
