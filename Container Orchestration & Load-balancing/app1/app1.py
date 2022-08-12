from flask import request, Flask
import socket
import os, subprocess


app1 = Flask(__name__)

@app1.route('/')

def hello_world():
 #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 #s.connect(("8.8.8.8", 80))
 #ip = s.getsockname()[0]
 #s.close()
 #ip = os.system('ip a | grep inet')
 hostname = socket.gethostname()
 ip = socket.gethostbyname(hostname)
 return 'Salam, this is App1 :)   '+ str(ip)



if __name__ == '__main__':
 app1.run(debug=True, host='0.0.0.0')

