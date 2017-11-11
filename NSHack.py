import urllib
from firebase import firebase
from flask import Flask, flash, redirect, render_template, request, session, abort
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import os
import json
import datetime
from forms import FirePut

app = Flask(__name__)
fb = firebase.FirebaseApplication('https://plusalpha-77c9d.firebaseio.com', None)

creditUsers = 'http://api.reimaginebanking.com/accounts?type=Credit%20Card&key=1d0ff9c1ed84ac0b6db1e1347a926c73'
accounts = 'http://api.reimaginebanking.com/accounts?key=1d0ff9c1ed84ac0b6db1e1347a926c73'

current_customerId = ''
current_accountId = ''

@app.route('/register', methods=['GET', 'POST'])
def form_example():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        newUser_id = request.form.get('newUser_id')
        newUser_pw = request.form['newUser_pw']
        newUser_firstname = request.form['newUser_first_name']
        newUser_lastname = request.form['newUser_last_name']

        # load creditcard users
        data = urllib.request.urlopen(creditUsers)
        response = data.read().decode('utf-8')
        content = json.loads(response)

        # find this new user has creditcard - account's firname and lastname should be matched
        isFound = False
        for result in content:
            print('id :', result['_id'])
            print('customer_id :', result['customer_id'])

            try:
                accounts = 'http://api.reimaginebanking.com/customers/' + result['customer_id'] + '?key=1d0ff9c1ed84ac0b6db1e1347a926c73'
                data2 = urllib.request.urlopen(accounts)
                response2 = data2.read().decode('utf-8')
                content2 = json.loads(response2)

                # if this user has creditcard, let user to register plusalpha
                if (content2['first_name'] == newUser_firstname and content2['last_name'] == newUser_lastname):
                    print('name: ', content2['first_name'])
                    fb.patch('/users/' + str(result['_id']),
                             {'newUser_firstname': newUser_firstname, 'newUser_lastname': newUser_lastname,
                              'newUser_pw': newUser_pw, 'savingAmount': 0, 'customer_id': result['customer_id'],
                              'account_id': result['_id']})
                    isFound = True

            except urllib.error.HTTPError as err:
                print(err.code)

        if(isFound == False):
            return "You have to have creditcard if you want to use PlusAlpha"
        else:
            return '''<h1>The newUser_id value is: {}</h1> 
                      <h1>The newUser_pw value is: {}</h1>'''.format(newUser_id, newUser_pw)

    return '''<form method="POST">
                  user ID: <input type="text" name="newUser_id"><br>
                  user first_name: <input type="text" name="newUser_first_name"><br>
                  user last_name: <input type="text" name="newUser_last_name"><br>
                  user PW: <input type="text" name="newUser_pw"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''

@app.route('/login', methods=['GET', 'POST'])
def form_login():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        newUser_firstname = request.form.get('newUser_firstname')
        newUser_lastname = request.form.get('newUser_lastname')
        newUser_pw = request.form['newUser_pw']

        userIds = fb.get('/users', None)
        for target in userIds:
            if(userIds[str(target)]['newUser_firstname'] == newUser_firstname and userIds[str(target)]['newUser_lastname'] == newUser_lastname and userIds[str(target)]['newUser_pw'] == newUser_pw):
                current_accountId = userIds[str(target)]['account_id']
                current_customerId = userIds[str(target)]['customer_id']
                return "Hello ! "+ newUser_firstname + " " + newUser_lastname  + "  <a href='/loan/"+ newUser_firstname +"'>Get Loan</a>   <br> <a href='/logout'>Logout</a>"
        return home()

    return '''<form method="POST">
                <h1>Login </h1>
                  user firstname: <input type="text" name="newUser_firstname"><br>
                  user lastname: <input type="text" name="newUser_lastname"><br>
                  userPW: <input type="text" name="newUser_pw"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''


@app.route('/loan/<name>', methods=['GET', 'POST'])
def loan_request(name):
    if request.method == 'POST':  # this block is only entered when the form is submitted
        # newUser_id = request.form.get('newUser_id')
        # newUser_pw = request.form['newUser_pw']
        # newUser_firstname = request.form['newUser_first_name']
        # newUser_lastname = request.form['newUser_last_name']

        user_requestAmount = request.form['amount']

        userIds = fb.get('/users', None)
        for target in userIds:
            if (str(target) != str(current_accountId) and float(userIds[str(target)]['savingAmount']) >= float(user_requestAmount)):
                print('found!!!! who has enough money: ', target)

                fb.patch('/users/' + str(result['_id']),
                         {'newUser_firstname': newUser_firstname, 'newUser_lastname': newUser_lastname,
                          'newUser_pw': newUser_pw, 'savingAmount': 0, 'customer_id': result['customer_id'],
                          'account_id': result['_id']})


                return "Hello ! " + name + " " +  " We found a person who can lend you the money.+ " + "  <br> <a href='/logout'>Logout</a>"
        return home()

    return '''<form method="POST">
                <h1>Hello, '''+ name + '''</h1>
                  request Loan amount: <input type="text" name="amount"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''


@app.route('/transaction/<account_id>', methods=['GET', 'POST'])
def transactionCheck(account_id):
    now = datetime.datetime.now()
    nowstr = str(now.year) + '-' + str(now.month) + '-' + str(now.day)

    print('nowstr : ', nowstr)
    print('acct:', account_id)

    # load the user's all transaction - purchases that you are involved in.
    purchases = 'http://api.reimaginebanking.com/accounts/' + str(account_id) + '/purchases?key=1d0ff9c1ed84ac0b6db1e1347a926c73'

    data = urllib.request.urlopen(purchases)
    response = data.read().decode('utf-8')
    content = json.loads(response)

    for result in content:
        if (result['purchase_date'] == nowstr):
            paidAmount = result['amount']
            saving = paidAmount * 0.05
            print('paid: ', paidAmount, ' saving: ', paidAmount * 0.05)

            # userinfo - update save amount
            userData = fb.get('/users/'+str(account_id), None)
            print('savingAmount ', userData['savingAmount'])

            fb.patch('/users/' + str(account_id), {'savingAmount': userData['savingAmount'] + saving})

# every mid-night system runs
@app.route('/run')
def checkAllTransaction():
    userIds = fb.get('/users', None)
    # print('here', userIds)
    for target in userIds:
        transactionCheck(target)
    return 'PlusAlpha - Daily Process is done.'
    # go to report page

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('/login.html')
    else:
        return "Hello Boss!  <a href='/logout'>Logout</a>"

# @app.route('/login', methods=['POST'])
# def do_admin_login():
#     result = fb.get('/users', None)
#     if request.form['password'] == result[request.form['username']]['newUser_pw']:
#         session['logged_in'] = True
#         print('success login: ', result[request.form['username']])
#     else:
#         flash('wrong password!')
#     return home()

# @app.route('/carduser', methods=['GET', 'POST'])
@app.route('/carduser')
def cardUser():
    data = urllib.request.urlopen(creditUsers)
    response = data.read().decode('utf-8')
    content = json.loads(response)

    for result in content:
        print(result['nickname'])

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return form_login()

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)


