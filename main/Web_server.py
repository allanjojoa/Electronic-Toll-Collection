#!/usr/bin/env python
import MySQLdb
from flask import *
from flask_mysqldb import MySQL
#import cv2
from Main import plate
import sys
#import os
#import os.path

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'plate_infomation'
app.config['MYSQL_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def root():
    return render_template('index.html')

#@app.route('/pla')
#def pla():
#    return plate

@app.route('/db')
def db():
    db = MySQLdb.connect("localhost","root","root","plate_information" )

    cursor = db.cursor()

    cursor.execute("SELECT * from plate_info")
    data = cursor.fetchall()    
    return render_template('db.html', data = data)
    db.close()

@app.route('/form', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('form.html')
        # show html form
        #return '''
        #    <form method="post">
        #        <input type="text" name="expression" />
        #       <input type="submit" value="Pay" />
        #   </form>
        #'''
    elif request.method == 'POST':
        # calculate result
        expression = request.form.get('expression')
        #result = eval(expression)
        db = MySQLdb.connect("localhost","root","root","plate_information" )
        cursor = db.cursor()
        cursor.execute("SELECT * from plate_info where due>0")
        data = cursor.fetchall()
        for row in data:
           if row[0]==expression:
              cursor.execute ("""UPDATE plate_info SET due=%s WHERE PLATE_NO=%s""", (0,expression))
              cursor.execute('''commit''')
              return 'Payed Due For %s' % expression
        return 'No Due'    
        db.close()
@app.route('/db_notzero')
def db2():
    db = MySQLdb.connect("localhost","root","root","plate_information" )

    cursor = db.cursor()

    cursor.execute("SELECT * from plate_info where due>0")
    data = cursor.fetchall()    
    return render_template('db.html', data = data)
    db.close()

@app.route('/about')
def about():
    return render_template('about.html')
#@app.route('/bal')
#def bal_def():
#    cur = mysql.connection.cursor()
#    cur.execute('''SELECT * FROM plate_info''')
#    due=-1
#    data = cur.fetchall()
#    for row in data:
#        if row[0]==plate:
#            due=row[1]
#            due=due+10
#            cur.execute ("""UPDATE plate_info SET due=%s WHERE reg_no=%s""", (due,plate))
#            cur.execute('''commit''')
#    return "Due on Plate:"+plate+" is "+str(due)

if __name__ == '__main__':
    app.run(threaded=True)
