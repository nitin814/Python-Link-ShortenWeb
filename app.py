
import random
import string

from flask import Flask , render_template , request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SECRET_KEY'] = '12345678'

url_dict = {}
with app.app_context():
    db = SQLAlchemy(app)

class table(db.Model):
    shortened_url = db.Column(db.String(400) , nullable = False)
    original_url = db.Column(db.String(400) , primary_key = True)

    def __repr__(self) -> str:
        return f"{self.shortened_url}  {self.original_url}"

with app.app_context():
    db.create_all()

def convert_to_dict(url_dict):
    return {i.shortened_url : i.original_url for i in url_dict}
def shortenurl():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(8))

@app.route('/' , methods=['GET' , 'POST'])
def generate_url():
    if request.method=='POST':
        originalurl = request.form['originalurl']
        shortenedurl = shortenurl()
        url_dict = table.query.all()
        url_dict=convert_to_dict(url_dict)
        if originalurl in url_dict.values():
            shortenedurl = list(url_dict.keys())[list(url_dict.values()).index(originalurl)]
            flash(request.url_root+shortenedurl)
            return render_template('index.html', shortenedurl=shortenedurl, originalurl=originalurl)
        while shortenedurl in url_dict:
            shortenedurl = shortenurl()
        url_dict[shortenedurl] = originalurl
        newrow = table(shortened_url = shortenedurl , original_url = originalurl)
        db.session.add(newrow)
        db.session.commit()
        flash(request.url_root+shortenedurl)
        return render_template('index.html', shortenedurl=shortenedurl, originalurl=originalurl)

    return render_template('index.html')

@app.route('/<short_url>')
def redirect_url(short_url):
    url_dict=table.query.all()
    url_dict=convert_to_dict(url_dict)
    url=url_dict.get(short_url)
    if url:
        return redirect(url)
    else:
        return f"URL doesn't exist"

@app.route('/allurls', methods=['GET' , 'POST'])
def allurls():
    if request.method=='POST':
        url_dict=table.query.all()
        return render_template('index2.html' , alllinks = url_dict, root=request.url_root);

if __name__ == "__main__":
    app.run(debug=True,port=8000)