from flask import Flask, render_template, session, redirect, url_for, request
import flask
import pymysql
from sqlalchemy import create_engine, exc, text
import sqlalchemy
import pandas as pd
import matplotlib.pyplot as plt
import os
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from dateutil import parser

app = Flask(__name__)

db = create_engine('mysql+pymysql://root:asky@35.192.119.6:3306/asky')
connection = db.connect()

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    # Example query
    # Get the search input from the JSON data

        # Example: Assuming you have a database connection and a cursor
    # cur = connection.execute("SELECT * FROM your_table WHERE column LIKE %s", ('%' + keyword + '%'))
    # results = cur.fetchall()

    # # For demonstration purposes, just return a simple response
    # results = f"Results for '{keyword}'"
    # return results


    # data = request.get_json()
    # keyword = data['keyword']

    #Read
    if "username" not in session:
        return redirect(url_for('login'))

    logname = session['username']

    weapon1 = flask.request.args.get("weapon1")
    area1 = flask.request.args.get("area1")
    weekday1 = flask.request.args.get("weekday1")

    query = {
        "weapon1": weapon1,
        "area1": area1,
        "weekday1": weekday1
    }


    if area1 is None:
        area1 = ''
    if weapon1 is None:
        weapon1 = ''
    if weekday1 is None:
        weekday1 = ''

    values = {'area': area1, 'wu' : weapon1, 'dow' : weekday1}
    cur = connection.execute(text('SELECT * FROM Crime_info WHERE AREA_CD = :area AND Weapon_Used_Cd = :wu AND Day_of_week = :dow'), values)

    result1 = cur.fetchall()
    
    # UPDATE

    weapon2 = flask.request.args.get("weapon2")
    area2 = flask.request.args.get("area2")
    weekday2 = flask.request.args.get("weekday2")
    dr2 = flask.request.args.get("dr2")

    query = {
        "weapon2": weapon2,
        "area2": area2,
        "weekday2": weekday2,
        "dr2": dr2
    }


    if area2 is None:
        area2 = ''
    if weapon2 is None:
        weapon2 = ''
    if weekday2 is None:
        weekday2 = ''
    if dr2 is None:
        dr2 = ''

    if area2 != '':
        values = {'a': area2, 'w' : weapon2, 'd' : weekday2, 'dr' : dr2}
        connection.execute(text('UPDATE Crime_info SET AREA_CD = :a, Weapon_Used_Cd = :w, Day_of_week = :d WHERE DR_NO = :dr'), values)

    #INSERT

    dr3 = flask.request.args.get("dr3")
    time3 = flask.request.args.get("time3")
    weekday3 = flask.request.args.get("weekday3")
    area3 = flask.request.args.get("area3")
    crm3 = flask.request.args.get("crm3")
    premis3 = flask.request.args.get("premis3")
    weapon3 = flask.request.args.get("weapon3")
    sex3 = flask.request.args.get("sex3")

    query = {
        "dr3": dr3,
        "time3": time3,
        "weekday3": weekday3,
        "area3": area3,
        "crm3": crm3,
        "premis3": premis3,
        "weapon3": weapon3,
        "sex3": sex3
    }


    if dr3 is None:
        dr3 = ''
    if time3 is None:
        time3 = ''
    if weekday3 is None:
        weekday3 = ''
    if area3 is None:
        area3 = ''
    if crm3 is None:
        crm3 = ''
    if premis3 is None:
        premis3 = ''
    if weapon3 is None:
        weapon3 = ''
    if sex3 is None:
        sex3 = ''

    if area3 != '':
        values = {'d': dr3, 't' : time3, 'wd' : weekday3, 'a' : area3, 'c' : crm3, 'p' : premis3, 'we' : weapon3, 's' : sex3}
        connection.execute(text("INSERT INTO Crime_info(DR_NO, TIME_OCC, Day_of_week, AREA_CD, CRM_CD, Premis_CD, Weapon_Used_Cd, Vict_Sex) VALUES (:d, :t, :wd, :a, :c, :p, :we, :s)"), values)

        values2 = {'u' : logname, 'd' : dr3}
        connection.execute(text("INSERT INTO User_input(username, DR_NO) VALUES (:u, :d)"), values2)

        connection.commit()

    # Creative Component

    area5 = flask.request.args.get("area5")

    if area5 is None:
        area5 = ''

    if area5 != '':
        val = {'ar' : area5}
        cur = connection.execute(text('SELECT COUNT(DR_NO), Day_of_week FROM Crime_info WHERE AREA_CD = :ar GROUP BY Day_of_week'), val)

        data = cur.fetchall()

        x = []
        y = []

        x.append("Mon")
        x.append("Tue")
        x.append("Wed")
        x.append("Thu")
        x.append("Fri")
        x.append("Sat")
        x.append("Sun")

        for i in data:
            y.append(i[0])

        df = pd.DataFrame(x, y)

        fig, ax = plt.subplots()

        ax.bar(x, y)

        ax.set_xlabel('Day of week')
        ax.set_ylabel('Crime Count')
        ax.set_title('Showing the crime count for specific Areas')

        fig.savefig('my_plot.png')

        plt.show()

        # ax = df.plot.bar(x='Day of week', y='Crime Count', rot=0)

    # Delete user input info

    dr4 = flask.request.args.get("dr4")

    if dr4 is None:
        dr4 = ''
    
    if dr4 != '':
        values = {"username" : logname, "dr_no" : dr4}
        connection.execute(text("CALL DeleteUserInput(:username, :dr_no)"), values)
        connection.commit()

    # Return all user input
    
    cur = connection.execute(text('SELECT max(DR_NO) FROM Crime_info'))

    dres = int(cur.fetchall()[0][0])

    values = {}
    cur = connection.execute(text('SELECT c.DR_NO, a.AREA_info, c.Day_of_week, w.Weapon_Desc FROM Crime_info c JOIN User_input u ON (c.DR_NO = u.DR_NO) JOIN Area a ON (a.AREA_CD = c.AREA_CD) JOIN Weapon w ON (w.Weapon_Used_Cd = c.Weapon_Used_Cd)'), values)

    # result1 = cur

    # result2 = result1[0]
    user_input = cur.fetchall()


    context = {
        "logname": logname,
        # "data": result2,
        # "all_data": result1,
        "area1": area1,
        "weapon1": weapon1,
        "weekday1": weekday1,
        "result": result1,
        "user_input" : user_input,
        "dres" : dres + 1,
    }

    print(context)
    return render_template('index.html', **context)



@app.route('/login.html', methods = ['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    msg = ''



    today_date = datetime.now()
    print(f"log today's date: {today_date}")

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        username = request.form['username']
        password = request.form['password']

        print('Attempted email: ' + username + ' | Attempted pass: ' + password)

        with db.connect() as conn:
             
            select_statement = "SELECT username, password FROM User_info WHERE username = :user"
            values = {'user': username}

            results = conn.execute(text(select_statement), values)

            for account in results:
                # print('DB Results:',account[0])
                # print('HASHED: ', str(bcrypt.generate_password_hash(password))[1:])
                if account:
                    print(account)
                    if bcrypt.check_password_hash(account[1], password):
                        session["username"] = username

                        return redirect(url_for('index', user=username))
                        # return render_template('dashboard.html', msg="", week_num = WEEK_NUM, att_sub = user_attendance, assign_link = user_assignments)
                        
                else:
                    msg = 'Incorrect username/password!'
                    print(msg)
                    return render_template('login.html', msg=msg)
    else:
        print("Not entering funct")          
        return render_template('login.html', msg="")
    return render_template('login.html', msg=msg)


@app.route('/register.html', methods = ['GET', 'POST'])
def register():
    # if session and session["loggedin"]:
    #     return redirect(url_for('dashboard'))

    if "username" in session:
        return redirect(url_for('index'))
    
    msg = ''

    today_date = datetime.now()
    print(f"reg today's date: {today_date}")

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'role' in request.form:

        print("Entered inside conditional")
        username = request.form['username']
        password = request.form['password']
        passwordrep = request.form['password-rep']
        role_type = request.form['role']

        print(username)
        print(password)
        print(passwordrep)
        print(role_type)

        if password!=passwordrep:
            msg = "Passwords don't match!"
            print(f"pass: {password} | passrep: {passwordrep}")
            return render_template('register.html', msg=msg)
        
        print(f"pass: {password} | passrep: {passwordrep}")

        with db.connect() as conn:

            select_statement = "SELECT * FROM User_info WHERE username = :user"
            values1 = {'user': username}
            results = conn.execute(text(select_statement), values1)

            print(results)

            for account in results:
                msg = "Email already registered!"
                return render_template('register.html', msg=msg)

            insert_statement = "INSERT INTO User_info(username, password, passwordrep, gender, age) VALUES (:user, :pass, :passr, :gend, :age)"
            values2 = {'user': username, 'pass': bcrypt.generate_password_hash(password).decode('utf-8'), 'passr': password, 'gend': role_type, 'age': 25}

            conn.execute(text(insert_statement).execution_options(autocommit=True), values2)

            conn.commit()

            # insert_statement2 = "INSERT INTO attendance(email_address, Workshop_1, Workshop_2, Workshop_3, Workshop_4, Workshop_5, Workshop_6, Workshop_7, Workshop_8) VALUES (:email_address, :Workshop_1, :Workshop_2, :Workshop_3, :Workshop_4, :Workshop_5, :Workshop_6, :Workshop_7, :Workshop_8)"
            # values3 = {'email_address': email, 'Workshop_1': '0', 'Workshop_2': '0', 'Workshop_3': '0', 'Workshop_4': '0', 'Workshop_5': '0', 'Workshop_6': '0', 'Workshop_7': '0', 'Workshop_8': '0'}
            # conn.execute(text(insert_statement2).execution_options(autocommit=True), values3)

            # insert_statement3 = "INSERT INTO assignments(email_address, Workshop_1, Workshop_2, Workshop_3, Workshop_4, Workshop_5, Workshop_6, Workshop_7, Workshop_8) VALUES (:email_address, :Workshop_1, :Workshop_2, :Workshop_3, :Workshop_4, :Workshop_5, :Workshop_6, :Workshop_7, :Workshop_8)"
            # values4 = {'email_address': email, 'Workshop_1': "", 'Workshop_2': "", 'Workshop_3': "", 'Workshop_4': "", 'Workshop_5': "", 'Workshop_6': "", 'Workshop_7': "", 'Workshop_8': ""}
            # conn.execute(text(insert_statement3).execution_options(autocommit=True), values4)

            # session['loggedin'] = True
            # session['id'] = username
            # session['email_address'] = email

            #TODO: REPLACE WITH LISTS
            # session['ATTENDANCE_SUBMITTED'] = False
            # session['ASSIGNMENT_SUBMITTED'] = False
            # session['ASSIGNMENT_LINK'] = ""

            print(username)
                            
            return redirect(url_for('index', user=username))
        
    return render_template('register.html', msg='')

@app.route("/logout.html", methods=['POST'])
def users_logout():
    """Log out user. Immediately redirect to /accounts/login/."""
    session.clear()
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)

