import urllib
from firebase import firebase
from flask import Flask, flash, redirect, render_template, request, session, abort
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import os
import json
import datetime

app = Flask(__name__)
fb = firebase.FirebaseApplication('https://plusalpha-77c9d.firebaseio.com', None)

creditUsers = 'http://api.reimaginebanking.com/accounts?type=Credit%20Card&key=1d0ff9c1ed84ac0b6db1e1347a926c73'
accounts = 'http://api.reimaginebanking.com/accounts?key=1d0ff9c1ed84ac0b6db1e1347a926c73'

current_customerId = ''
current_accountId = ''
current_name = ''
current_name2 = ''

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
    return render_template('register.html')
    # return '''<form method="POST">
    #              <h1>+@ PlusAlpha. Save for "even" more!</h1>
    #               user ID: <input type="text" name="newUser_id"><br>
    #               user first_name: <input type="text" name="newUser_first_name"><br>
    #               user last_name: <input type="text" name="newUser_last_name"><br>
    #               user PW: <input type="text" name="newUser_pw"><br>
    #               <input type="submit" value="Submit"><br>
    #           </form>'''

@app.route('/login', methods=['GET', 'POST'])
def form_login():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        newUser_firstname = request.form.get('newUser_firstname')
        newUser_lastname = request.form.get('newUser_lastname')
        newUser_pw = request.form['newUser_pw']

        userIds = fb.get('/users', None)
        for target in userIds:
            if(userIds[str(target)]['newUser_firstname'] == newUser_firstname and userIds[str(target)]['newUser_lastname'] == newUser_lastname and userIds[str(target)]['newUser_pw'] == newUser_pw):
                global current_customerId
                global current_accountId
                global current_name
                global current_name2
                current_accountId = userIds[str(target)]['account_id']
                current_customerId = userIds[str(target)]['customer_id']
                current_name = newUser_firstname
                current_name2 = newUser_firstname

        return render_template('home.html')

    return render_template('login.html')



@app.route('/loanSuccess', methods=['GET', 'POST'])
def loan_result(count):
    global current_customerId
    global current_accountId
    global current_name

    return render_template('loanSuccess.html', cnt=str(count))


@app.route('/loan', methods=['GET', 'POST'])
def loan_request():
    global current_customerId
    global current_accountId
    global current_name
    name = current_name

    if request.method == 'POST':
        user_requestAmount = request.form['amount']
        count = 0
        possible = []

        userIds = fb.get('/users', None)
        for target in userIds:
            if (str(target) != str(current_accountId) and float(userIds[str(target)]['savingAmount']) >= float(user_requestAmount)):
                count+= 1
                if(count == 1):
                    curr = fb.get('/users/' + str(current_accountId), None)
                    subtotal = float(user_requestAmount) + (float(user_requestAmount) * 0.25)

                    fb.patch('/loan/' + str(current_accountId),
                             {'newUser_firstname': name, 'borrower_accountId': str(current_accountId), 'borrower_customerId': str(current_customerId),
                              'lender_accountID': str(target), 'requestAmount': float(user_requestAmount), 'loanTotal':subtotal })
                possible.append( {'key':str(target), 'amount':float(userIds[str(target)]['savingAmount']) })

        if(count == 0):
            return home()
        else:
            fb.patch('/users/' + str(possible[0]['key']), {'savingAmount':  float(possible[0]['amount']) -  float(user_requestAmount) })
            return loan_result(count)
            # return render_template('loanSuccess.html', cnt=str(count))
            # return "Hello ! " + name + " " + " We found " + str(count) + "people who can lend you the money. <br> We chose best lender for you. " \
            #                                                              "<br> The money is deposited.+ " + "  <br> <a href='/home'>Home</a>   <br> <a href='/logout'>Logout</a>"

    # return '''<form method="POST">
    #             <h1>+@ PlusAlpha. Save for "even" more! Hello, '''+ name + '''</h1>
    #               request Loan amount: <input type="text" name="amount"><br>
    #               <input type="submit" value="Submit"><br>
    #           </form>'''
    return render_template('loan.html', usernm=str(name))


@app.route('/payback', methods=['GET', 'POST'])
def payback():
    global current_customerId
    global current_accountId
    global current_name

    loan = 100
    lender = ''
    original = 0
    add = 0

    curr = fb.get('/loan', None)
    for key, value in curr.items():
        if (key == str(current_accountId)):
            loan = value['loanTotal']
            lender = str(value['lender_accountID'])
            original = value['requestAmount']
    #
    adds = fb.get('/users/'+lender, None)
    for key, value in adds.items():
        if(key == 'savingAmount'):
            add = float(value)

    if request.method == 'POST':  # this block is only entered when the form is submitted
        user_requestAmount = request.form['amount']
        # userIds = fb.get('/loan/'+str(current_accountId), None)
        remain = original
        curr = fb.get('/loan', None)
        for key, value in curr.items():
            if(key == str(current_accountId)):
                remain = float(value['loanTotal']) - float(user_requestAmount)
                fb.patch('/loan/' + str(current_accountId), {'loanTotal': remain})
                print(current_accountId,'remain -----------', remain)
                loan = remain + (remain * 0.25)

                add += float(user_requestAmount)
                fb.patch('/users/' + str(lender), {'savingAmount': add})

        return render_template('payback.html', original=str(remain), loan=str(loan))
        # return '''<form method="POST">
        #                 <h1>+@ PlusAlpha. Save for "even" more! <br> Hello, ''' + current_name + '''</h1>
        #                   The amount borrowed $ ''' + str(remain) + ''' <br>
        #                   Total amount include interest $ ''' + str(loan) + ''' <br>
        #                   Intrest rate is 25% <br>
        #                   How much money you want to pay back?: <input type="text" name="amount"><br>
        #                   <input type="submit" value="Submit"><br>
        #               </form>
        #               <a href='/home'>Home</a>
        #               '''
    return render_template('payback.html', original=str(original), loan=str(loan) )

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

    return ''

# every mid-night system runs
@app.route('/run')
def checkAllTransaction():
    userIds = fb.get('/users', None)
    for target in userIds:
        transactionCheck(target)
    return render_template('runResult.html', userName=str(current_name) + " " + str(current_name2))
    # return '+@ PlusAlpha. Save for "even" more! - Daily Process is done. <br> <a href="/home">Home</a>  '
    # go to report page

@app.route('/')
def home():
    if not session.get('logged_in'):
        return "+@ PlusAlpha. Save for even more!! <br> <a href='/login'>Login</a> <br> "
        # return render_template('/login.html')
    else:
        return "Hello! +@ PlusAlpha. Save for even more! <br><a href='/login'>Login</a> <br>  <a href='/logout'>Logout</a> <br>"

@app.route('/home')
def home_myaccount():
    global current_names
    global current_name2

    return render_template('home.html', userName=str(current_name)+" "+str(current_name2))

    # return "+@ PlusAlpha. Save for even more! <br> " + str(current_name) + " " + str(current_name2) +" <br>
    # <a href='/loan/"+ current_name +"'>Get Loan</a> <br> <a href='/payback>Pay Back</a>  <br> <a href='/logout'>Logout</a>"

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
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=80)