from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '12e89e9ef18af3a03e5b819ac2c4ff1c'  # Замените на свой секретный ключ


# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('whatsapp_numbers.db')
    conn.row_factory = sqlite3.Row
    return conn


# Создание таблиц, если они не существуют
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            messenger TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Главная страница
@app.route('/')
def index():
    conn = get_db_connection()
    numbers = conn.execute('SELECT * FROM numbers').fetchall()
    conn.close()
    return render_template('index.html', numbers=numbers)


# Регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким именем уже существует.', 'error')
        finally:
            conn.close()

    return render_template('register.html')


# Авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль.', 'error')

    return render_template('login.html')


# Выход пользователя
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


# Добавление номера
@app.route('/add', methods=['POST'])
def add_number():
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для добавления номеров.', 'error')
        return redirect(url_for('login'))

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
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для удаления номеров.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM numbers WHERE id = ?', (number_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()  # Инициализация базы данных при запуске приложения
    app.run(debug=True)
