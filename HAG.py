from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session


# Create a database connection to an SQLite database
def create_sqlite_database(filename):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        # Create a database called account_details if it doesn't exist
        query1 = ("CREATE TABLE IF NOT EXISTS account_details "
                  "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  "f_name TEXT, l_name TEXT, email TEXT, psw TEXT, location TEXT);")  # the information that will be  saved in this databse
        cursor.execute(query1)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


# saves the data that the user used to sign up in the account_details
def save_data(filename, f_name, l_name, email, psw, location):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        # Use parameterized query to avoid SQL injection
        query3 = ("INSERT INTO account_details (f_name, l_name, email, psw, location) "
                  "VALUES (?, ?, ?, ?, ?);")
        cursor.execute(query3, (f_name, l_name, email, psw, location))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def list_data(filename):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        query = "SELECT * FROM account_details"
        result = cursor.execute(query)
        data = result.fetchall()
        conn.commit()
        return data
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


# Route for te home page
@app.route("/home")
def home():
    create_sqlite_database("account_details.db")
    return render_template('main.html')


# Route for the login page
@app.route("/", methods=['GET', 'POST'])
def login():
    create_sqlite_database("account_details.db")
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["psw"]
        user_exists, user_role = login_user("account_details.db", email, password)

        if user_exists == "valid":
            session["email"] = email
            return redirect(url_for("home"))  # Redirect to main after login
        else:
            return render_template("login.html", status="Invalid username or password, try again")
    return render_template('login.html')


# Function to log in a user
def login_user(filename, email, password):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM account_details WHERE email = ? AND psw = ?", (email, password))
        user = cursor.fetchone()

        if user:
            return "valid", [2]
        else:
            return "invalid", None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "error", None
    finally:
        if conn:
            conn.close()


# Route for the sign up pa
@app.route("/signup")
def signup():
    return render_template("signup.html")


# Route for the signup page (Data saving)
@app.route("/signup", methods=['POST'])
def signupost():
    f_name = request.form["f_name"]
    l_name = request.form["l_name"]
    email = request.form["email"]
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2 ,}$', email)
    return "Valid" if valid else "Make sure your email its correct"
    password = request.form["psw"]
    location = request.form["location"]
    # Save the user data to the database
    save_data("account_details.db", f_name, l_name, email, password, location)
    return render_template("login.html", people=list_data("account_details.db"))


# Route for the about page
@app.route("/about")
def about():
    return render_template('about.html')


# Route for the weather page
@app.route("/weather")
def weather():
    return render_template('weather.html')


# Route for the health page
@app.route("/health")
def health():
    email = session.get('email')
    return render_template("health.html", h_data=health_advice("account_details.db", email), uem=(email))


# rdata will be used to in the HTML file.


# SQL txo show data in a meaningfull way
def health_advice(filename, email):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        query = "SELECT  account_details.f_name,account_details.l_name, WeatherCondition.Condition FROM account_details,Health_Advice,WeatherCondition WHERE account_details.id = Health_Advice.AdviceID AND Health_Advice.Advice = WeatherCondition.WeatherConditionID AND account_details.email = '" + email + "'"
        result = cursor.execute(query)
        data = result.fetchall()
        conn.commit()
        return data
    except sqlite3.Error as e:
        return e
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    # Initialize the database

    app.run()
