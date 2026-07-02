from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    unique_id = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.String(20), default="Not Started")

    def __repr__(self):
        return '<Task %r>' % self.id 


@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        existing_ids = {t.unique_id for t in Todo.query.all()}
        new_unique_id = 1
        while new_unique_id in existing_ids:
            new_unique_id += 1
        
        new_task = Todo(content=task_content, unique_id=new_unique_id)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except: 
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task.'


@app.route('/update/<int:id>', methods = ['POST', 'GET'])
def update(id):
    task = Todo.query.get_or_404(id)
    
    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating the task'
    else:
        return render_template('update.html', task=task)


@app.route('/search', methods=['GET']) 
def search():
    query = request.args.get('q', '').strip()

    if not query:
        return render_template('search.html', tasks=[])
    
    try:
        uid = int(query)
    except ValueError:
        uid = None

    tasks = Todo.query.filter(
        (Todo.content.ilike(f"%{query}%")) |
        (Todo.unique_id == uid)
    ).order_by(Todo.date_created).all()

    return render_template('search.html', tasks=tasks)

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id): 
    task = Todo.query.get_or_404(id)
    new_status = request.form.get('status')

    task.status = new_status
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)