from flask import Flask, jsonify, request
import datetime
import sqlite3

app = Flask(__name__)


@app.route('/')
def home():
    return 'Welcome to the NASCAR API!'


# Find out if a Race is on a specific Day and Time
@app.route('/race')
def get():
    date = request.args.get('date', None)
    time = request.args.get('time', None)

    # Validate Date
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date() if date else None
    except ValueError:
        date_obj = None

    # Validate Time
    try:
        time_obj = datetime.datetime.strptime(time, "%H:%M:%S").time() if time else None
    except ValueError:
        time_obj = None

    # Date Message
    if not date_obj:
        date_message = 'Invalid date entry.'
    elif date_obj == datetime.datetime.today().date():
        date_message = 'There’s a race on this day!'
    else:
        date_message = 'Sorry, no race on this day.'

    # Time Message
    if not time_obj:
        time_message = 'Invalid time entry.'
    elif datetime.time(17, 0, 0) <= time_obj <= datetime.time(20, 0, 0):
        time_message = 'There’s a race during this time!'
    else:
        time_message = 'Sorry, no race during this time.'

    return jsonify({
        'race': {
            'date': {'entered': date, 'message': date_message},
            'time': {'entered': str(time), 'message': time_message}
        }
    })


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


@app.route('/season/cup')
def season():
    # If no 'year' is given, set year to current year
    year = request.args.get('year', datetime.datetime.now().strftime("%Y"))

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
