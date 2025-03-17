from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
USER_DATA_FILE = 'users.txt'

def save_user(username, password, paypal_name, paypal_email, initial_balance=0.0):
    with open(USER_DATA_FILE, 'a') as f:
        f.write(f"{username},{password},{paypal_name},{paypal_email},{initial_balance}\n")

def get_user_data(username):
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            user_data = line.strip().split(',')
            if user_data[0] == username:
                return user_data
    return None

def update_paypal_info(username, paypal_name, paypal_email):
    with open(USER_DATA_FILE, 'r') as f:
        users = f.readlines()
    with open(USER_DATA_FILE, 'w') as f:
        for user in users:
            if user.startswith(username):
                data = user.strip().split(',')
                f.write(f"{username},{data[1]},{paypal_name},{paypal_email},{data[4]}\n")
            else:
                f.write(user)

def update_balance(username, new_balance):
    with open(USER_DATA_FILE, 'r') as f:
        users = f.readlines()
    with open(USER_DATA_FILE, 'w') as f:
        for user in users:
            if user.startswith(username):
                data = user.strip().split(',')
                data[-1] = str(new_balance)
                f.write(','.join(data) + "\n")
            else:
                f.write(user)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="static/images/icon.png" type="image/png">
    <title>StreamLet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background-color: #00aa95; color: white; }
        header { background-color: #007f77; padding: 20px; text-align: center; }
        a { color: white; text-decoration: none; margin: 0 15px; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <header><h1>Welcome to StreamLet</h1></header>
    <p><a href="/login">Login</a> | <a href="/signup">Sign Up</a></p>
</body>
</html>'''

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        paypal_name = request.form['paypal_name']
        paypal_email = request.form['paypal_email']
        
        save_user(username, password, paypal_name, paypal_email, initial_balance=0.0)
        session['username'] = username
        flash("Successfully signed up!", "success")
        return redirect(url_for('dashboard'))
    
    return '''(similar to the signup HTML code above for simplicity)'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = get_user_data(username)
        
        if user_data and user_data[1] == password:
            session['username'] = username
            flash("Successfully logged in!", "success")
            return redirect(url_for('dashboard'))
        else:
            error_message = "Invalid username or password."
    
    return '''(similar to the login HTML code above for simplicity)'''

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_data = get_user_data(session['username'])
    balance = user_data[-1] if user_data else 0.0
    return f'''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="static/images/icon.png" type="image/png">
    <title>StreamLet | Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background-color: #00aa95; color: white; }}
        header {{ background-color: #007f77; padding: 20px; }}
        main {{ padding: 40px; text-align: center; }}
        button {{ padding: 10px 20px; border: none; background-color: #007f77; color: white; }}
    </style>
</head>
<body>
    <header><h1>Your Dashboard</h1></header>
    <main>
        <h2>Balance: {balance}€</h2>
        <button id="watchAdButton">Watch Ad</button>
        <button onclick="location.href='/logout'">Logout</button>
    </main>
</body>
</html>'''

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Successfully logged out!", "success")
    return redirect(url_for('index'))

@app.route('/search_user')
def search_user():
    username_query = request.args.get('username', '')
    results = []
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            user_data = line.strip().split(',')
            if username_query.lower() in user_data[0].lower():
                results.append({'username': user_data[0], 'balance': user_data[-1]})
    return {'results': results}

@app.route('/user/<username>')
def user_details(username):
    user_data = get_user_data(username)
    if user_data:
        return f'''
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="icon" href="static/images/icon.png" type="image/png">
    <title>StreamLet | User Details</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #00aa95; color: white; }}
        header {{ background-color: #007f77; padding: 20px; }}
    </style>
</head>
<body>
    <header><h1>User Details: {user_data[0]}</h1></header>
    <main>
        <p>Balance: {user_data[4]}€</p>
        <input type="number" id="amount" placeholder="Amount to send" required>
        <button id="sendButton">Send Money</button>
        <p id="message"></p>
    </main>
    <script>
        document.getElementById('sendButton').onclick = function() {{
            const amount = document.getElementById('amount').value;
            fetch('/send_money', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    receiver_username: '{user_data[0]}',
                    amount: amount
                }})
            }}).then(response => response.json()).then(data => {{
                document.getElementById('message').innerText = data.message;
            }});
        }};
    </script>
</body>
</html>'''
    else:
        flash("User not found!", "error")
        return redirect(url_for('index'))

@app.route('/send_money', methods=['POST'])
def send_money():
    data = request.get_json()
    sender_username = session['username']
    receiver_username = data.get('receiver_username', None)
    amount = data.get('amount', None)

    sender_data = get_user_data(sender_username)
    receiver_data = get_user_data(receiver_username)
    
    if not sender_data or not receiver_data:
        return {'message': 'User not found'}, 404

    sender_balance = float(sender_data[-1])
    
    if float(amount) > sender_balance:
        return {'message': 'Insufficient funds.'}, 400
    
    new_sender_balance = sender_balance - float(amount)
    update_balance(sender_username, new_sender_balance)
    
    new_receiver_balance = float(receiver_data[-1]) + float(amount)
    update_balance(receiver_username, new_receiver_balance)

    return {'message': f'Successfully sent {amount}€ to {receiver_username}'}

if __name__ == '__main__':
    app.run(debug=True)
