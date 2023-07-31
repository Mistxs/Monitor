import mysql.connector
import sqlite3
import datetime
import time

def execute_mysql_query():
    # Подключение к базе данных MySQL
    mysql_conn = mysql.connector.connect(
        host='your_mysql_host',
        user='your_mysql_user',
        password='your_mysql_password',
        database='your_mysql_database'
    )
    mysql_cursor = mysql_conn.cursor()

    # Выполнение запроса MySQL
    mysql_query = """
    SELECT ttt1.*
    FROM tt_timeslots ttt1
    JOIN tt_timeslots ttt2 ON ttt1.master_id = ttt2.master_id
    WHERE ttt1.dt_from >= ttt2.dt_from
    AND ttt1.dt_to <= ttt2.dt_to
    AND ttt1.id <> ttt2.id
    AND ttt1.dt_to > '2023-07-15'
    AND ttt1.master_id IN (SELECT id FROM masters WHERE salon_id = 162492 AND deleted = 0)
    GROUP BY 1
    """
    mysql_cursor.execute(mysql_query)
    mysql_rows = mysql_cursor.fetchall()
    num_rows = len(mysql_rows)

    # Закрытие подключения к базе данных MySQL
    mysql_conn.close()

    # Подключение к базе данных SQLite
    sqlite_conn = sqlite3.connect('mydatabase.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Запись результатов в таблицу SQLite
    current_time = datetime.datetime.now()
    sqlite_cursor.execute("INSERT INTO query_results (execution_time, num_rows) VALUES (?, ?)",
                          (current_time, num_rows))
    sqlite_conn.commit()

    # Закрытие подключения к базе данных SQLite
    sqlite_conn.close()

    # Вывод результатов
    print(f"Запрос выполнен за {datetime.datetime.now() - current_time} секунд")
    print(f"Количество строк: {num_rows}")

# Бесконечный цикл для выполнения запроса и записи результатов в SQLite каждые 10 минут
while True:
    execute_mysql_query()
    time.sleep(600)  # Подождите 10 минут перед следующим выполнением запроса