import sqlite3

# Create/Connect to db
db = sqlite3.connect('nascar_api.db')

# Create cursor
cursor = db.cursor()
cursor.execute('PRAGMA foreign_keys = ON')

# Create Races Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Races (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER,
        name TEXT NOT NULL,
        series TEXT NOT NULL,
        date TEXT NOT NULL,
        winner TEXT,
        FOREIGN KEY (track_id) REFERENCES Racetracks (id)
    )
''')

# Enter Data
while True:
    track_id = input('Enter Track ID: ')
    name = input('Enter Race Name: ')
    series = input('Enter Race Series: ')
    date = input('Enter Race Date YYYY/MM/DD: ')

    try:
        cursor.execute('INSERT into Races (track_id, name, series, date, winner) VALUES('
                       ':track_id, '
                       ':name, '
                       ':series, '
                       ':date,  '
                       'NULL '
                       ')',
                       {'track_id': track_id,
                        'name': name,
                        'series': series,
                        'date': date
                        })
        db.commit()
    except sqlite3.IntegrityError:
        print('Error.')
    else:
        print('Success!')
