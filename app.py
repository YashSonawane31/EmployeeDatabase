from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
import os
import uuid

app = Flask(__name__)

if not 'RUNNING_IN_PRODUCTION' in os.environ:
   # Local development, where we'll use environment variables.
   print("Loading config.development and environment variables from .env file.")
   app.config.from_object('azureproject.development')
else:
   # Production, we don't load environment variables from .env file but add them as environment variables in Azure.
   print("Loading config.production.")
   app.config.from_object('azureproject.production')

def get_db_connection():
    return psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=pwd,
        port=port_id
    )

try:
    conn = psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute('DROP TABLE IF EXISTS employee')

    create_script = ''' CREATE TABLE IF NOT EXISTS employee(
                            id     int PRIMARY KEY,
                            name   varchar(40) NOT NULL,
                            emp_id int) '''
    
    cur.execute(create_script)
    conn.commit()

except Exception as error:
    print(error)

finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()

@app.route('/', methods=['GET'])
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
    webbrowser.open('http://localhost:5000')
    app.run()
