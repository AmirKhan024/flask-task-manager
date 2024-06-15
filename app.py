from flask import Flask,render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import os

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///task.db"
app.config["SECRET_KEY"]=os.urandom(24)

db=SQLAlchemy(app)

ist=pytz.timezone("Asia/Kolkata")
def current_time():
    return datetime.now(ist)

class TaskManager(db.Model):
    taskId=db.Column(db.Integer, primary_key=True)
    taskName=db.Column(db.String(200), nullable=False)
    taskDesc=db.Column(db.String(500), nullable=False)
    date=db.Column(db.DateTime,default=current_time)
    completed=db.Column(db.Boolean,default=False)

    def __repr__(self) -> str:
        return f"{self.taskId}-{self.taskName}"
    
@app.route("/", methods=["GET","POST"])
def index():
    if(request.method=='POST'):
        taskName=request.form['title']
        taskDesc=request.form['desc']
        if not taskName or not taskDesc:
            flash("Please enter both task name and description","danger")
        else:
            task=TaskManager(taskName=taskName,taskDesc=taskDesc)
            db.session.add(task)
            db.session.commit()
            flash("Task added successfully!","success")
    allTask=TaskManager.query.all()
    return render_template("index.html",allTask=allTask)

@app.route("/search/",methods=["GET","POST"])
def search_task():
    if(request.method=='POST'):
        search=request.form['search_query']
        search_result=TaskManager.query.filter(TaskManager.taskName.like("%"+search+"%")| TaskManager.taskDesc.like("%"+search+"%")).all()
        return render_template("index.html",allTask=search_result)
    
@app.route("/update/<int:taskId>", methods=['GET','POST'])
def update(taskId):
    if(request.method=='POST'):
        taskName=request.form['title']
        taskDesc=request.form['desc']
        if not taskName or not taskDesc:
            flash("Please enter both task name and description","danger")
        else:
            task=TaskManager.query.filter_by(taskId=taskId).first()
            task.taskName=taskName
            task.taskDesc=taskDesc
            db.session.add(task)
            db.session.commit()
            return redirect("/")
    updateTask=TaskManager.query.filter_by(taskId=taskId).first()
    return render_template("update.html",allTask=updateTask)

@app.route("/delete/<int:taskId>", methods=['GET','POST'])
def delete(taskId):
    task=TaskManager.query.filter_by(taskId=taskId).first()
    db.session.delete(task)
    db.session.commit()
    
    return redirect("/")

@app.route("/update_status/<int:taskId>",methods=["POST"])
def status(taskId):
    task=TaskManager.query.filter_by(taskId=taskId).first()
    if task:
        task.completed=not task.completed
        db.session.commit()
    return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)