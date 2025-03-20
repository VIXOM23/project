from flask import Flask, redirect, render_template, url_for, flash
from forms import RegistrationForm, LoginFrom

app = Flask(__name__)
app.config["SECRET_KEY"] = 'Mashakakasha'

@app.route("/")
@app.route("/home")
def home():
    return render_template("homepage.html", title="Домашняя страница")

@app.route('/about')
def about():
    return "<h1>Welcome to about page<h1>"

@app.route('/login', methods = ["GET", "POST"])
def login():
    form = LoginFrom()
    
    return render_template('login.html', title = 'login', form = form)

@app.route('/register', methods = ["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title = 'Register', form = form)
    

if __name__ == "__main__":
    app.run(debug=True)