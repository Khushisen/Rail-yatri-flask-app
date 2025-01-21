from flask import Flask,render_template,request,flash,redirect,url_for
import requests
import pymysql
import secrets
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

def get_db_connection():
    
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        port=3306,
        database='railway'
    )
load_dotenv()
app=Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        flash("Login successful!","success")
        return redirect(url_for('home'))  # Redirect to home page

    return render_template('login.html')
                
    
    
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email=request.form['email']
        password=request.form['password']
        
        if not username or not email or not password:
            flash("All fields are required!", "error")
            return redirect(url_for('signup'))
        
        connection = None
        cursor = None
        try:
            connection=get_db_connection()
            cursor=connection.cursor()
            # Insert the user into the database
            query = "INSERT INTO login (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            connection.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('signup'))
        except pymysql.MySQLError as e:
            if connection and connection.open:
                connection.rollback()
            flash("Error: Unable to create account. Username or email might already exist.", "error")
            print(f"MySQL Error: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
         
    return render_template('signup.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/pnr',methods=['GET','POST'])
def pnr():
    if request.method=='POST':
        data=request.form.get('pnr')
        print('Data ',data)
        url = f"https://irctc-indian-railway-pnr-status.p.rapidapi.com/getPNRStatus/{data}"

        headers = {
	    "x-rapidapi-key": "9aa2d44274msh55fc767a2614668p1fb690jsn8164e7ba4207",
	    "x-rapidapi-host": "irctc-indian-railway-pnr-status.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        result = response.json()
        print(result)
        if  result['success'] == True:
            d={
                'Date of Journey':result['data']['dateOfJourney'],
                'Train Number' : result['data']['trainNumber'],
                'Train Name': result['data']['trainName'],
                'Source Station': result['data']['sourceStation'],
                'Destination Point': result['data']['boardingPoint'],
                'No of passengers': result['data']['numberOfpassenger']
                }
            passenger=[]
            for i in result['data']['passengerList']:
                passenger.append([i['passengerSerialNumber'],i['bookingStatusDetails'],i['currentStatusDetails']])
            return render_template('pnr.html',d=d,passenger=passenger)
        else:
            return render_template('pnr.html',msg='No Such PNR Found')
        return 'success'
    else:
        return render_template('pnr.html')
@app.route('/track')
def track():
    return render_template('track.html')

if __name__=='__main__':
    app.run('localhost',50000,debug=True)