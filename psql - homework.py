import psycopg2

def drop_tables(cur):
    cur.execute("""
            DROP TABLE IF EXISTS User_Number;
            DROP TABLE IF EXISTS Users;
            DROP TABLE IF EXISTS Numbers;
    """)

def create_tables(cur, conn):
    cur.execute("""
            CREATE TABLE IF NOT EXISTS Users(
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(40) UNIQUE,
                last_name VARCHAR(40) UNIQUE,
                email VARCHAR(40) UNIQUE);
                
            CREATE TABLE IF NOT EXISTS Numbers(
                id SERIAL PRIMARY KEY,
                number VARCHAR(80) UNIQUE);
                
            CREATE TABLE IF NOT EXISTS User_Number(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES Users(id),
                number_id INTEGER REFERENCES Numbers(id));
            """)
    conn.commit()

def add_user(cur, data, conn):
    cur.execute(f"""
            INSERT INTO Users(first_name, last_name, email)
            VALUES('{data[0]}', '{data[1]}', '{data[2]}') 
            RETURNING first_name;
    """)
    print(f'Пользователь {cur.fetchone()[0]} был добавлен в базу данных')

def __add_info__(cur, user_id, number_id):
    cur.execute(f"""
            INSERT INTO User_Number(user_id, number_id)
            VALUES({user_id}, {number_id});
    """)
    print('Номер добавлен')

def __find_user__(cur, data=None):
    cur.execute(f"""
            SELECT id FROM Users WHERE first_name='{data[0]}' AND last_name='{data[1]}';
    """)
    return(int(cur.fetchone()[0]))

def add_number(cur, number, data):
    cur.execute(f"""
            INSERT INTO Numbers(number)
            VALUES('{number}')
            RETURNING id;
    """)
    number_id = int(cur.fetchone()[0])
    user_id = __find_user__(cur, data)
    __add_info__(cur, user_id, number_id)

def change_data(cur, old_data, new_data, conn):
    user_id = __find_user__(cur, old_data)
    cur.execute(f"""
            UPDATE Users SET first_name='{new_data[0]}' WHERE id={user_id};
            UPDATE Users SET last_name='{new_data[1]}' WHERE id={user_id};
            UPDATE Users SET email='{new_data[2]}' WHERE id={user_id};
    """)
    conn.commit()
    print('Данные были успешно обновлены.')

def del_user(cur, user_name):
    user_id = __find_user__(cur, user_name)
    cur.execute(f"""
            SELECT number_id FROM User_Number WHERE user_id = {user_id}
    """)
    number_id = int(cur.fetchone()[0])
    cur.execute(f"""
            DELETE FROM Users WHERE id={user_id};
            DELETE FROM User_Number WHERE user_id ={user_id};
            DELETE FROM Numbres WHERE id={number_id};
    """)
    print(f'Пользователь {user_name} был успешно удалён.')

def del_number(cur, user_name, number):
    user_id = __find_user__(cur, user_name)
    cur.execute(f"""
            SELECT id FROM Numbers WHERE number = {number}
        """)
    number_id = int(cur.fetchone()[0])
    cur.execute(f"""
            DELETE FROM Numbers WHERE id={number_id};
            DELETE FROM User_Number WHERE user_id={user_id} AND number_id={number_id};
    """)
    print('Номер удалён.')

def find_user_by_data(cur, user_name):
    user_id = __find_user__(cur, user_name)
    cur.execute(f"""
            SELECT u.id, u.first_name, u.last_name, u.email, n.number FROM Users u 
            JOIN User_Number un ON u.id = un.user_id
            RIGHT JOIN Numbers n ON un.number_id = n.id
            WHERE U.id={user_id}
    """)
    print(cur.fetchone())

in_ = ''
with psycopg2.connect(database="user_database", user="postgres", password='133766') as conn:
    with conn.cursor() as cur:
        drop_tables(cur)
        create_tables(cur, conn)
        while in_ != 'quit':
            in_ = input('Введите команду (для помощи введите help): ')
            if in_ == 'help':
                print('add_user - добавить пользователя;\nadd_number - добавить номер пользователя;\nchange_data - изменить данные пользователя;\ndel_user - удалить пользователя;\ndel_number - удалить номер пользователя;\nfind_user - найти данные пользователя;\nquit - выйти из программы.')
            elif in_ == 'add_user':
                data = input('Введите Имя, Фамилию, почту через пробел: ').split(' ')
                add_user(cur, data, conn)
            elif in_ == 'add_number':
                data = input('Введите Имя, Фамилию нужного аккаунта через пробел: ').split(' ')
                number = int(input('Введите номер телефона: '))
                add_number(cur, number, data)
            elif in_ == 'change_data':
                data = input('Введите Имя, Фамилию нужного аккаунта через пробел: ').split(' ')
                new_data = input('Введите новые Имя, Фамилию, почту аккаунта через пробел: ').split(' ')
                change_data(cur, data, new_data, conn)
            elif in_ == 'del_user':
                data = input('Введите Имя, Фамилию нужного аккаунта через пробел: ').split(' ')
                del_user(cur, data)
            elif in_ == 'del_number':
                data = input('Введите Имя, Фамилию нужного аккаунта через пробел: ').split(' ')
                number = int(input('Введите удаляемый номер телефона: '))
            elif in_ == 'find_user':
                data = input('Введите Имя, Фамилию нужного аккаунта через пробел: ').split(' ')
                find_user_by_data(cur, data)
            elif in_ == 'quit':
                break
            else:
                print('Введена неизвестная команда.')
conn.close()
