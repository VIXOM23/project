from flask import Flask, redirect, render_template, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('homepage.html', title = "Домашняя страница")


if __name__ == '__main__':
    app.run(debug=True)