from flask import Flask, render_template
from flask_restful import Api, reqparse
import mysql.connector

app = Flask(__name__)
api = Api(app)
data = []
connection = ''
cursor = ''


def db_connector():
    global connection
    global cursor
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'library',
        'auth_plugin': 'mysql_native_password'
    }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(buffered=True)


parser = reqparse.RequestParser()


@app.route('/register/', methods=['POST'])
def register_users():
    parser.add_argument('name', type=str)
    parser.add_argument('phone', type=str)
    parser.add_argument('password', type=str)
    args = parser.parse_args()
    db_connector()
    temp = 'INSERT INTO user (name,Phone_Number,Password) VALUES (%s,%s,%s)'
    # return temp
    cursor.execute(temp, (args['name'], args['phone'], args['password']))
    connection.commit()
    cursor.close()
    connection.close()
    return "Success user registration!"


@app.route('/check/', methods=['POST'])
def check_users():
    parser.add_argument('phone', type=str)
    parser.add_argument('password', type=str)
    args = parser.parse_args()
    temp = 'SELECT Password FROM user WHERE Phone_Number=%(pn)s'
    db_connector()
    cursor.execute(temp, {'pn': args['phone']})
    ret_str = ''

    if cursor.rowcount <= 0:
        ret_str = "This user is not exist"

    # return results[0]
    else:
        results = cursor.fetchone()
        if results[0] == args['password']:
            ret_str = "Wellcome!"
        else:
            ret_str = "Wrong password!!"

    cursor.close()
    connection.close()
    return ret_str


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/check-user")
def index_check():
    return render_template('Check_User.html')


@app.route("/create-user")
def index_register():
    return render_template('Create_User.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
