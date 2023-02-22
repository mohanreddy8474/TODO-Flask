from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import dateparser
from datetime import datetime

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    complete = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date)
    days = db.Column(db.Text)

    def __repr__(self):
        return f"Todo   ('{self.id}', '{self.title}','{self.complete}', '{self.date}', '{self.days})"


@app.route("/", methods=['GET', 'POST'])
def home():
    todo_list = Todo.query.all()
    return render_template("home.html", todo_list=todo_list)


@app.route("/add", methods=["GET", "POST"])
def add():
    title = request.form.get("title")
    date = dateparser.parse(request.form.get('date')).date()
    delta = date - datetime.now().date()
    if delta.days == 0:
        days = f"{delta.days} days left"
    elif delta.days < -1:
        days = f"{abs(delta.days)} days Over Due"
    elif delta.days == -1:
        days = f"{abs(delta.days)} day over Due"
    elif delta.days == 1:
        days = f"{abs(delta.days)} day left"
    else:
        days = f"{delta.days} days left"
    new_todo = Todo(title=title, complete=False, date=date, days=days)
    db.session.add(new_todo)
    db.session.commit()
    todo_list = Todo.query.all()
    return render_template("home.html", todo_list=todo_list)


@app.route("/update/<int:todo_id>", methods=["GET", "POST"])
def update(todo_id):
    todo = Todo.query.get(todo_id)
    if request.method == 'POST':
        todo.title = request.form.get("title")
        todo.date = dateparser.parse(request.form["date"]).date()
        delta = todo.date - datetime.now().date()
        if delta.days == 0:
            todo.days = f"{delta.days} days left"
        elif delta.days < -1:
            todo.days = f"{abs(delta.days)} days Over Due"
        elif delta.days == -1:
            todo.days = f"{abs(delta.days)} day over Due"
        elif delta.days == 1:
            todo.days = f"{abs(delta.days)} day left"
        else:
            todo.days = f"{delta.days} days left"
        db.session.commit()
        return redirect('/')
    else:
        return render_template("update.html", todo=todo)


@app.route("/complete/<int:todo_id>")
def complete(todo_id):
    todo = Todo.query.get(todo_id)
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/deleteall")
def deleteall():
    todo_list = Todo.query.all()
    for i in todo_list:
        db.session.delete(i)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/sort", methods=["POST"])
def sort():
    if request.method == "POST":
        todo_list = Todo.query.order_by(Todo.date).all()
        return render_template("home.html", todo_list=todo_list)
    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():
    if request.method == "POST":
        a = request.form.get('a')
        ab = a
        todo_list = Todo.query.filter(Todo.title.ilike(f"%{a}%")).all()
        return render_template("home.html", todo_list=todo_list, ab=ab)
    return render_template("home.html")


@app.route("/display", methods=["POST"])
def display():
    if request.method == "POST":
        date = dateparser.parse(request.form["date"]).date()
        todo_list = Todo.query.filter(Todo.date == date).all()
        return render_template("home.html", todo_list=todo_list)
    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()
