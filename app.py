from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Strong random secret key for session
USER_DATA_FILE = 'users.txt'  # Path to user data file

# Function to save user data
def save_user(username, password, paypal_name, paypal_email, initial_balance=0.0):
    with open(USER_DATA_FILE, 'a') as f:
        f.write(f"{username},{password},{paypal_name},{paypal_email},{initial_balance}\n")

# Function to get user data by username
def get_user_data(username):
    if not os.path.exists(USER_DATA_FILE):
        return None  # Return None if user file doesn't exist
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            user_data = line.strip().split(',')
            if user_data[0] == username:
                return user_data  # Return the entire user data
    return None  # Return None if user is not found

# Home Page
@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="{{ url_for('static', filename='images/icon.png') }}" type="image/png">
    <title>StreamLet</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #00aa95; color: white; }
        header { background-color: #007f77; padding: 15px 20px; text-align: center; }
        nav a { color: white; margin: 0 15px; text-decoration: none; }
        main { padding: 20px; text-align: center; }
    </style>
</head>
<body>
    <header>
        <h1>StreamLet</h1>
        <nav>
            <a href="{{ url_for('login') }}">Login</a>
            <a href="{{ url_for('signup') }}">Sign Up</a>
        </nav>
    </header>
    <main>
        <h1>Welcome to StreamLet</h1>
        <p>Earn money by watching ads!</p>
        <a href="{{ url_for('signup') }}">Get Started</a>
    </main>
</body>
</html>
    """)

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        paypal_name = request.form['paypal_name']
        paypal_email = request.form['paypal_email']
        
        # Save the user's details with an initial balance of 0.0
        save_user(username, password, paypal_name, paypal_email, initial_balance=0.0)
        session['username'] = username 
        flash("Successfully signed up!", "success")
        return redirect(url_for('dashboard'))  # Redirect to dashboard after signing up
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StreamLet | Sign Up</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #00aa95; color: white; }
        header { background-color: #007f77; padding: 15px 20px; text-align: center; }
        main { padding: 40px; }
        h1 { font-size: 2.5em; }
        form { display: flex; flex-direction: column; }
        input { padding: 10px; margin-bottom: 15px; border: none; border-radius: 5px; }
        button { padding: 10px; background-color: #007f77; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <header>
        <h1>StreamLet</h1>
    </header>
    <main>
        <h1>Create an Account</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="text" name="paypal_name" placeholder="PayPal Name" required>
            <input type="email" name="paypal_email" placeholder="PayPal Email" required>
            <button type="submit">Sign Up</button>
        </form>
        <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a>.</p>
    </main>
</body>
</html>
    """)

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = get_user_data(username)
        
        if user_data is not None and user_data[1] == password:
            session['username'] = username
            flash("Successfully logged in!", "success")
            return redirect(url_for('dashboard'))
        else:
            error_message = "Invalid username or password. Please try again."
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StreamLet | Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #00aa95; color: white; }
        header { background-color: #007f77; padding: 15px 20px; text-align: center; }
        main { padding: 40px; }
    </style>
</head>
<body>
    <header>
        <h1>Login</h1>
    </header>
    <main>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
            {% if error_message %}
                <p>{{ error_message }}</p>
            {% endif %}
        </form>
        <p>Don't have an account? <a href="{{ url_for('signup') }}">Sign Up</a>.</p>
    </main>
</body>
</html>
    """)

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in

    user_data = get_user_data(session['username'])
    balance = 0.0
    if user_data:
        balance = user_data[-1]  # Get the balance

    return render_template_string(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #00aa95; color: white; }}
        header {{ background-color: #007f77; padding: 15px 20px; text-align: center; }}
        main {{ padding: 40px; }}
        .balance {{ padding: 10px; font-weight: bold; }}
    </style>
</head>
<body>
    <header>
        <h1>Your Dashboard</h1>
    </header>
    <main>
        <p>Your Balance: <span class="balance">{balance} €</span></p>
        <a href="{{ url_for('paypal') }}">Update PayPal Info</a><br>
        <a href="{{ url_for('search') }}">Search Users</a><br>
        <a href="{{ url_for('pro') }}">Pro Features</a><br>
        <a href="{{ url_for('logout') }}">Logout</a>
    </main>
</body>
</html>
    """)

# PayPal Info Page
@app.route('/paypal', methods=['GET', 'POST'])
def paypal():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in
    if request.method == 'POST':
        paypal_name = request.form['paypal_name']
        paypal_email = request.form['paypal_email']
        # Update PayPal info (you would want to implement updating logic here)
        flash("PayPal information updated successfully!", "success")
        return redirect(url_for('dashboard'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>StreamLet | PayPal Info</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #00aa95; color: white; }
        header { background-color: #007f77; padding: 15px 20px; text-align: center; }
        main { padding: 40px; }
    </style>
</head>
<body>
    <header>
        <h1>PayPal Information</h1>
    </header>
    <main>
        <form method="POST">
            <input type="text" name="paypal_name" placeholder="PayPal Name" required>
            <input type="email" name="paypal_email" placeholder="PayPal Email" required>
            <button type="submit">Update Info</button>
        </form>
        <p><a href="{{ url_for('dashboard') }}">Back to Dashboard</a></p>
    </main>
</body>
</html>
    """)

# Search User Page
@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StreamLet | Search Users</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #00aa95; color: white; }
        header { background-color: #007f77; padding: 15px 20px; text-align: center; }
        main { padding: 40px; }
        input { padding: 10px; margin-bottom: 20px; border: none; border-radius: 5px; }
        button { padding: 10px; background-color: #007f77; color: white; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <header>
        <h1>Search Users</h1>
    </header>
    <main>
        <input type="text" id="searchInput" placeholder="Enter username" />
        <button id="searchButton">Search</button>
        <div class="user-list" id="userList"></div>  <!-- User results will be rendered here -->
        <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    </main>

    <script>
        document.getElementById('searchButton').addEventListener('click', function() {
            const username = document.getElementById('searchInput').value;
            const userList = document.getElementById('userList');
            userList.innerHTML = ""; // Clear previous results

            fetch(`/search_user?username=${encodeURIComponent(username)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.results.length > 0) {
                        data.results.forEach(user => {
                            const userDiv = document.createElement('div');
                            userDiv.innerHTML = `<strong>${user.username}</strong> - ${user.balance} €`;
                            userList.appendChild(userDiv);
                        });
                    } else {
                        userList.innerHTML = "<p>No users found.</p>";
                    }
                })
                .catch(err => {
                    console.error(err);
                    userList.innerHTML = "<p>Error fetching users.</p>";
                });
        });
    </script>
</body>
</html>
    """)

# User Details Page
@app.route('/user/<username>')
def user_details(username):
    user_data = get_user_data(username)
    if user_data:
        return render_template_string(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>User Details</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #00aa95; color: white; }}
        header {{ background-color: #007f77; padding: 15px 20px; text-align: center; }}
        main {{ padding: 40px; }}
    </style>
</head>
<body>
    <header>
        <h1>User Details</h1>
    </header>
    <main>
        <p>Username: {user_data[0]}</p>
        <p>Balance: {user_data[4]} €</p>
        <p><input type="number" id="amount" placeholder="Amount to send" required></p>
        <button id="sendButton">Send Money</button>
        <p id="message"></p>
        <a href="{{ url_for('search') }}">Back to Search</a>
    </main>

    <script>
        document.getElementById('sendButton').addEventListener('click', function() {
            const amount = parseFloat(document.getElementById('amount').value);
            const username = "{user_data[0]}"; // Get the username from the context
            
            // Send money request to server
            fetch('/send_money', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ receiver_username: username, amount: amount }),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('message').innerText = data.message; // Show the response message
            })
            .catch(err => {
                console.error(err);
                document.getElementById('message').innerText = 'An error occurred while attempting to send money. Please try again later.';
            });
        });
    </script>
</body>
</html>
        """)
    else:
        return redirect(url_for('search'))

# Send Money Endpoint
@app.route('/send_money', methods=['POST'])
def send_money():
    data = request.json
    sender_username = session['username']
    receiver_username = data.get('receiver_username')
    amount = data.get('amount')

    sender_data = get_user_data(sender_username)
    receiver_data = get_user_data(receiver_username)

    if sender_data is None or receiver_data is None:
        return {'message': 'User not found'}, 404

    sender_balance = float(sender_data[-1])
    if amount > sender_balance:
        return {'message': 'Insufficient funds.'}, 400

    # Proceed with sending money
    new_sender_balance = sender_balance - amount
    new_receiver_balance = float(receiver_data[-1]) + amount

    # Update the balances in the user data file
    update_balance(sender_username, new_sender_balance)
    update_balance(receiver_username, new_receiver_balance)

    return {'message': f'Successfully sent €{amount} to {receiver_username}'}

# Helper function to update user balances
def update_balance(username, new_balance):
    with open(USER_DATA_FILE, 'r') as f:
        users = f.readlines()
    
    with open(USER_DATA_FILE, 'w') as f:
        for user in users:
            if user.startswith(username):
                data = user.strip().split(',')
                data[-1] = str(new_balance)  # Update the balance
                f.write(','.join(data) + "\n")
            else:
                f.write(user)

# Pro Features Page
@app.route('/pro')
def pro():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>StreamLet | Pro Features</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #00aa95; color: white; }
        header { background-color: #007f77; padding: 15px 20px; text-align: center; }
        main { padding: 40px; }
    </style>
</head>
<body>
    <header>
        <h1>Pro Features</h1>
    </header>
    <main>
        <p>Activate the bot to earn credits by spending time on this page!</p>
        <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    </main>
</body>
</html>
    """)

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Successfully logged out!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
