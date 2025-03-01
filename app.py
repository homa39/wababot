from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('whatsapp_numbers.db')
    conn.row_factory = sqlite3.Row
    return conn


# Главная страница
@app.route('/')
def index():
    conn = get_db_connection()
    numbers = conn.execute('SELECT * FROM numbers').fetchall()
    conn.close()
    return render_template('index.html', numbers=numbers)


# Добавление номера
@app.route('/add', methods=['POST'])
def add_number():
    phone_number = request.form['phone_number']
    messenger = request.form['messenger']
    price = request.form['price']

    conn = get_db_connection()
    conn.execute('INSERT INTO numbers (phone_number, messenger, price) VALUES (?, ?, ?)',
                 (phone_number, messenger, price))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# Удаление номера
@app.route('/delete/<int:number_id>')
def delete_number(number_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM numbers WHERE id = ?', (number_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
