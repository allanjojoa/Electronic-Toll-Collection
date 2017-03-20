#!/usr/bin/env python
from flask import *
from flask_mysqldb import MySQL
import cv2
import Main
import sys
import os
import os.path
from flask_mysqldb import MySQL

found=False
src = 0
cap = cv2.VideoCapture(1)

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'plate_info'
app.config['MYSQL_HOST'] = 'localhost'
mysql.init_app(app)
 

#if len(sys.argv) < 2:
#    print "Format: python <prog_name> <filename>\n"
#    os.system("pause")
#    sys.exit()

#filename=sys.argv[-1]
try:
    os.remove("static/imgOriginalScene.png")
except:
    print 'No file to Remove\n'

print 'Detecting\n'
plate='none'
while found==False:
    ret, filename= cap.read()
    plate=Main.main(filename)
    found=os.path.exists("static/imgOriginalScene.png")
# create app
print 'Found\n'
#app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')

@app.route('/bal')
def bal_def():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM plate_info''')
    due=-1
    data = cur.fetchall()
    for row in data:
        if row[0]==plate:
            due=row[1]
            due=due+10
            cur.execute ("""UPDATE plate_info SET due=%s WHERE reg_no=%s""", (due,plate))
            cur.execute('''commit''')
    return "Due on Plate:"+plate+" is "+str(due)

if __name__ == '__main__':
    app.run()
