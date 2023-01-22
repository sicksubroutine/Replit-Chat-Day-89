import os
from flask import Flask, request, redirect
from replit import db
import datetime
app = Flask(__name__, static_url_path='/static')

admin_user_ID = os.environ['userID']

def getChats(userID):
  keys = db.keys()
  keys = list(keys)
  keys.sort()
  keys = keys[-5:]
  with open("chat_msg.html", "r") as f:
    message = f.read()
  res = ""
  for key in keys:
    key_time = datetime.datetime.fromtimestamp(float(key))
    key_time = key_time.strftime("%I:%M:%S %p")
    myMessage = message
    myMessage = myMessage.replace("{username}", db[key]["userName"])
    myMessage = myMessage.replace("{chat_msg}", db[key]["message"])
    myMessage = myMessage.replace("{pfp}", db[key]["userImage"])
    myMessage = myMessage.replace("{timestamp}", key_time)
    if userID == admin_user_ID:
      myMessage = myMessage.replace("{admin}", f"""<a href="/delete/?id={key}"> ❌</a>""")
    else:
      myMessage = myMessage.replace("{admin}", "")
    res += myMessage
  return res
@app.route("/")
def login():
  if request.headers["X-Replit-User-Name"]:
    return redirect("/chat")
  page = ""
  with open("login.html", "r") as f:
    page = f.read()
  return page

@app.route("/chat", methods=["GET"])
def chat():
  results = request.args.get("res")
  if results is None:
    results = ""
  if not request.headers["X-Replit-User-Name"]:
    return redirect("/")
  userID = request.headers["X-Replit-User-ID"]
  page = f"{results}"
  with open("chat.html", "r") as f:
    page += f.read()
    page = page.replace("{chat_msg}", getChats(userID))
  return page

@app.route("/add", methods=["POST"])
def add():
  if not request.headers["X-Replit-User-Name"]:
    return redirect("/")
  form = request.form
  message = form["message"]
  date = datetime.datetime.now()
  timestamp = datetime.datetime.timestamp(date)
  userName = request.headers["X-Replit-User-Name"]
  userID = request.headers["X-Replit-User-ID"]
  userImage = request.headers["X-Replit-User-Profile-Image"]
  db[timestamp] = {"userid": userID, "userName": userName, "message": message, "userImage": userImage}
  return redirect("/chat")

@app.route("/delete/", methods=["GET"])
def delete():
  if request.headers["X-Replit-User-ID"] != admin_user_ID:
    return redirect("/")
  else:
    results = request.args.get("id")
    if results is None:
      return redirect("/chat?res=delete failure")
    del db[results]
    return redirect("/chat?res=delete success")
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)