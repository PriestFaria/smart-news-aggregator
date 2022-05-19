from flask import Flask, render_template, request, redirect, flash, session, url_for
from werkzeug import exceptions
from flask_sqlalchemy import SQLAlchemy
import datetime, json, random
from training import train as train_func
#from parser import main as parse
app = Flask(__name__)

app.secret_key = "08d2c95c904805ba5a56e2c01fa58e26e50dc3654a8a704601459cfa916cab5"
app.permanent_session_lifetime = 60 * 60
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///base.db'
db = SQLAlchemy(app)


def logged():
    if 'user' in session.keys():
        return True
    return False


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(40), nullable=False)
    picked_news = db.Column(db.String())
    training_set = db.Column(db.String())

    def __repr__(self):
        return '%r' % self.name

class Article(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    link = db.Column(db.String(500),nullable=False)
    title = db.Column(db.String(300),nullable=False)
    image = db.Column(db.String(1000))
    date = db.Column(db.String(30), nullable=False)
    insider = db.Column(db.String(100),nullable=False)
    def __repr__(self):
        return f"{self.title}"

def commit_articles_to_db(articles_file_path):
        
    with open(articles_file_path,'r') as f:    
        arr = json.load(f)["articles"]
        for i in arr:
            if bool(Article.query.filter_by(title=i['title']).first()):
                continue
            else:
                article = Article(title=i['title'],link=i['link']
                            ,image=i['image'],date=i['date']
                            ,insider=i['insider'])
                db.session.add(article)
    
                
        db.session.commit()


@app.route("/clear_db")
def clear_db():
    session.clear
    db.session.query(User).delete()
    db.session.commit()
    return render_template('index.html')


@app.route('/')
def index():
    return render_template("index.html", users=User.query.all(),logged=logged())


@app.route('/sign-in', methods=["POST", "GET"])
def sign_in():
    if request.method == "POST":
        try:
            if bool(User.query.filter_by(name=request.form['name']).first()):
                flash("user already exists")
                return redirect(url_for("sign_in"))
            else:
                if request.form['name'] == "" or request.form['password'] == "":
                    flash("You should fill all fields")
                    return redirect(url_for("sign_in"))
                else:
                    user = User(name=request.form['name']
                            , password=request.form['password'])
                    db.session.add(user)
                    db.session.commit()
                    flash("Successful signed in!")
                    return redirect('/')
        except:
            flash("Oops, something went wrong!")
            return redirect('/')
    else:
        if "user" in session.keys(): del session['user']
        return render_template("sign_in.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            if bool(User.query.filter_by(name=request.form['name']).first()):

                if User.query.filter_by(name=request.form['name']).first().password== request.form['password']:
                    session["user"] = request.form['name']
                    session["picked"] = ''
                    session['train']={}
                    flash("Successfully logged in!")
                    return redirect(url_for("index"))
                else:
                    flash("Incorrect username or password")
                    return redirect(url_for("login"))

            else:
                if request.form['name'] == "" or request.form['password'] == "":
                    flash("You should fill all fields")
                    return redirect(url_for("login"))
                else:
                    flash("Incorrect username or password")
                    return redirect(url_for("login"))
        except:
            flash("Oops, something went wrong!")
            return redirect(url_for("index"))
    else:
        if "user" in session.keys(): del session['user']
        return render_template("login.html")


@app.route("/news")
def news():
    if not logged():
        #return render_template("please_login.html")
        return render_template("news.html",news_list=list(set(random.choices(Article.query.all(),k=200))), logged=logged())
    else:
        neural = train_func(session['user'])
        if neural == 0:
            return render_template("news.html",
                news_list=list(set(random.choices(Article.query.all(),k=200))),
                logged=logged())
        #news = random.choices(Article.query.all(),k=150)
        news = list(set(random.choices(Article.query.all(),k=200)))
        to_show = []
        for i in news:
            print(i.title)
            if (neural[0].predict_proba(neural[1].transform([str(i.title)])))[0][0] >= 0.9:
                to_show.append(i)
        return render_template("news.html",news_list=to_show, logged=logged())
 

@app.route("/train", methods=["POST","GET"])
def train():
    if not logged():
        return render_template("please_login.html")
    else:
        
        try:
            request.form['train']
            interesting = [title[1:-1] for title in session['picked']
                        .split("|||")]
            session['train_db'] = {
                    "interesting": interesting,

                    "not_interesting":
                        [article['title'] for article in session['train_list']
                            if not article['title'] in interesting]
}
            del session['train_list']
            with open("users.json","r") as users_json:
                json_dict = json.load(users_json)
                try:
                    json_dict[session['user']] = {
                        "interesting":list(set(json_dict[session['user']]["interesting"]
                        + session['train_db']["interesting"])),
                        "not_interesting":list(set(json_dict[session['user']]["not_interesting"]
                        + session["train_db"]["not_interesting"]))
                        }
                except KeyError:
                    json_dict[session['user']] = session['train_db']
            with open("users.json",'w') as users_json:
                json.dump(json_dict,users_json,indent=6)
            return redirect(url_for('index'))
        except exceptions.BadRequestKeyError:
            session['train_db'] = {} 
            if request.method == "POST":    
                session['picked'] += (request.get_data(as_text=True)) + "|||"
                return render_template("train.html"
                        ,logged=logged()
                        ,train_list=session['train_list'])
 
            elif request.method == "GET":
                
                session['picked'] = ''
                session['train_list'] = random.choices(
                    [dict(
                            title=article.title,
                            image=article.image,
                            link=article.link,
                            insider=article.insider,
                            date=article.date
                        ) for article in Article.query.all()]
                        ,k=18)
                
                return render_template("train.html"
                        ,logged=logged()
                        ,train_list=session['train_list'])
            
@app.route('/logout')
def logout():
    del session["user"]
    return redirect(url_for("index"))

    
    
if __name__ == "__main__":
    commit_articles_to_db("articles.json")
    #parse('articles.txt')
    app.run()
