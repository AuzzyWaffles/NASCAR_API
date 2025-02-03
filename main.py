from flask import Flask, jsonify, request, render_template
import datetime
import sqlite3
import os

app = Flask(__name__)
API_KEY = os.getenv('API_KEY')


# Home
@app.route('/')
def home():
    return render_template('home.html')


# Post races to a specific Season by Year
@app.route('/post', methods=['POST'])
def post_season_data():
    key = request.headers.get('X-API-KEY')
    if key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json

    track_id = data.get('track_id')
    name = data.get('name')
    series = data.get('series')
    date = data.get('date')
    winner = data.get('winner')
    year = data.get('year')

    if not year or not track_id or not name or not series or not date:
        return jsonify({'error': 'Invalid Data'}), 400

    # Create/Connect to db
    db = sqlite3.connect('nascar_api.db')

    # Create cursor
    cursor = db.cursor()

    # Create Races Season Table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS Races_{year} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            name TEXT NOT NULL,
            series TEXT NOT NULL,
            date TEXT NOT NULL,
            winner TEXT,
            FOREIGN KEY (track_id) REFERENCES Racetracks (id)
        )
    ''')

    try:
        cursor.execute(f'INSERT into Races_{year} (track_id, name, series, date, winner) VALUES('
                       ':track_id, '
                       ':name, '
                       ':series, '
                       ':date,  '
                       ':winner '
                       ')',
                       {'track_id': track_id,
                        'name': name,
                        'series': series,
                        'date': date,
                        'winner': winner
                        })
        db.commit()
    except sqlite3.Error as e:
        return jsonify({f'error': e}), 400
    else:
        return jsonify({'success': f'Data posted to Races_{year}'}), 201
    finally:
        db.close()


# Get track names based on State
@app.route('/track')
def track_by_state():
    state = request.args.get('state', None)

    # Connect to db and assign cursor
    db = sqlite3.connect('nascar_api.db')
    db.row_factory = sqlite3.Row  # Allows access by column name
    cursor = db.cursor()

    # Get Tracks based on State
    try:
        cursor.execute('SELECT name FROM Racetracks WHERE state = ?', (state,))
        result = cursor.fetchall()

        # Convert result to a list of track names
        track_names = [row['name'] for row in result]

        return jsonify({'message': f'The following racetracks are in {state}: {track_names}'})

    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

    finally:
        db.close()


# Get Cup season schedule based on year
@app.route('/season/cup')
def season():
    # If no 'year' is given, set year to current year
    year = request.args.get('year', datetime.datetime.now().strftime('%Y'))

    # Connect to db and assign cursor
    db = sqlite3.connect('nascar_api.db')
    db.row_factory = sqlite3.Row  # Allows access by column name
    cursor = db.cursor()

    # Get schedule based on year
    try:
        cursor.execute(f'SELECT Racetracks.name AS track, Races_{year}.name AS race_name, Races_{year}.series, '
                       f'Races_{year}.date, Races_{year}.winner '
                       f'FROM Races_{year} '
                       f'JOIN Racetracks ON Races_{year}.track_id = Racetracks.id')
        data = cursor.fetchall()
        json = {'season': []}

        for row in data:
            json['season'].append({'track': row['track'],
                                   'name': row['race_name'],
                                   'series': row['series'],
                                   'date': row['date'],
                                   'winner': row['winner']})

        return jsonify(json)
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
