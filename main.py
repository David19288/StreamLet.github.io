from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"
USER_FILE = "users.txt"
RECAPTCHA_SECRET_KEY = "6Lc_LOQqAAAAAEG1HtenB_wW2WfuOOp1HSvA0yPx"


def save_user(username, password):
    with open(USER_FILE, "a") as f:
        f.write(f"{username},{password}\n")

def user_exists(username):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, "r") as f:
        return any(line.split(",")[0] == username for line in f)

def check_credentials(username, password):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, "r") as f:
        return any(line.strip() == f"{username},{password}" for line in f)

def verify_recaptcha(response):
    payload = {"secret": RECAPTCHA_SECRET_KEY, "response": response}
    r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    return r.json().get("success", False)

HOME_PAGE = """
<html>
<head>
    <title>Streamlet - Earn from Ads</title>
    <style>
        body { background-color: #00aa95; color: white; text-align: center; font-family: Arial; }
        .button { background-color: yellow; color: black; padding: 15px 25px; border: none; border-radius: 10px; cursor: pointer; font-size: 18px; }
        .button:hover { background-color: orange; }
    </style>
</head>
<body>
    <h1>Welcome to Streamlet</h1>
    <p>Watch ads and earn 10% of the revenue!</p>
    <a href="/signup" class="button">Sign Up</a>
    <a href="/login" class="button">Login</a>
</body>
</html>
"""

SIGNUP_PAGE = """
<html>
<head>
    <title>Sign Up</title>
    <style>
        body { background-color: #00aa95; color: white; text-align: center; font-family: Arial; }
        .form-container { padding: 20px; border-radius: 10px; background: white; color: black; display: inline-block; }
        input { padding: 10px; margin: 5px; border-radius: 5px; border: none; }
        .button { background-color: yellow; color: black; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .button:hover { background-color: orange; }
    </style>
</head>
<body>
    <h1>Sign Up</h1>
    <div class="form-container">
        <form method="post">
            Username: <input type="text" name="username" required><br>
            Password: <input type="password" name="password" required><br>
            <script src="https://www.google.com/recaptcha/api.js" async defer></script>
            <div class="g-recaptcha" data-sitekey="YOUR_RECAPTCHA_SITE_KEY"></div><br>
            <input type="submit" value="Sign Up" class="button">
        </form>
    </div>
    <br><a href="/login">Already have an account? Login</a>
</body>
</html>
"""

LOGIN_PAGE = """
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    <form method="post">
        Username: <input type="text" name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_PAGE)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        recaptcha_response = request.form.get("g-recaptcha-response")
        
        if not verify_recaptcha(recaptcha_response):
            flash("Please verify you are not a robot!", "error")
        elif user_exists(username):
            flash("Username already taken! Try another.", "error")
        else:
            save_user(username, password)
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
    
    return render_template_string(SIGNUP_PAGE)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        
        if check_credentials(username, password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!", "error")
    
    return render_template_string(LOGIN_PAGE)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return f"<h1>Welcome, {session['user']}!</h1><br><a href='/logout'>Logout</a>"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
