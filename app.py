from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import os
import uuid

from requests import RequestException

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# If RUNNING_IN_PRODUCTION is defined as an environment variable, then we're running on Azure
if not 'RUNNING_IN_PRODUCTION' in os.environ:
   # Local development, where we'll use environment variables.
   print("Loading config.development and environment variables from .env file.")
   app.config.from_object('azureproject.development')
else:
   # Production, we don't load environment variables from .env file but add them as environment variables in Azure.
   print("Loading config.production.")
   app.config.from_object('azureproject.production')

with app.app_context():
    app.config.update(
        SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM employee ORDER BY id ASC')
    employees = cur.fetchall()
    conn.close()
    return render_template('index.html', employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT MAX(id) FROM employee')
        max_id = cur.fetchone()[0]
        new_id = 1 if max_id is None else max_id + 1
        cur.execute('INSERT INTO employee (id, name, emp_id) VALUES (%s, %s, %s)', (new_id, name, emp_id))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/edit_employee/<int:id>')
def edit_employee(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM employee WHERE id = %s', (id,))
    employee = cur.fetchone()
    conn.close()
    return render_template('edit.html', employee=employee)

@app.route('/save_employee/<int:id>', methods=['POST'])
def save_employee(id):
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE employee SET name = %s, emp_id = %s WHERE id = %s', (name, emp_id, id))
        conn.commit()
        conn.close()

    return redirect(url_for('index'))

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM employee WHERE id = %s', (id,))
    cur.execute('UPDATE employee SET id = id - 1 WHERE id > %s', (id,)) 
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
