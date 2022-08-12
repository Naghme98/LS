from flask import request, Flask
import socket

app2 = Flask(__name__)


@app2.route('/')


def hello_world():
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect(("8.8.8.8", 80))
# ip = s.getsockname()[0]
# s.close()
#  ip = os.system('ip a | grep inet')
 hostname = socket.gethostname()
 ip = socket.gethostbyname(hostname)
 return 'Salam, this is App2 :)   '+ str(ip)

if __name__ == '__main__':
 app2.run(debug=True, host='0.0.0.0')

