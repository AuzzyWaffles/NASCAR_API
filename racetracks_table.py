import sqlite3

# Create/Connect to db
db = sqlite3.connect('nascar_api.db')


# Create cursor
cursor = db.cursor()
cursor.execute('PRAGMA foreign_keys = ON')

# Create Racetracks Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Racetracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        length FLOAT NOT NULL,
        type INTEGER NOT NULL,
        state TEXT NOT NULL
    )
''')

# Enter Data
while True:
    name = input('Enter Track Name: ')
    length = float(input('Enter Track Length: '))
    type = input('Enter Track Type: ')
    state = input('Enter Track State: ')

    try:
        cursor.execute('INSERT into Racetracks (name, length, type, state) VALUES('
                       ':name, '
                       ':length, '
                       ':type, '
                       ':state '
                       ')',
                       {'name': name,
                        'length': length,
                        'type': type,
                        'state': state
                        })
        db.commit()
    except sqlite3.IntegrityError:
        print('Error.')
    else:
        print('Success!')
