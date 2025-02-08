from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Table

import os
import sqlite3
import datetime
from collections import defaultdict

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABADE_URI'] = 'sqlite:///nascar_api.db'
API_KEY = os.getenv('API_KEY')

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)


# Define Racetracks table model
class Racetrack(db.Model):
    __tablename__ = 'Racetracks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    length = db.Column(db.Float, nullable=False)
    type = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)


# Define Races table model
def dynamic_races_table(year):
    class Race(db.Model):
        __tablename__ = f'Races_{year}'

        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        track_id = db.Column(db.Integer, db.ForeignKey('Racetracks.id'))
        name = db.Column(db.String, nullable=False)
        series = db.Column(db.String, nullable=False)
        date = db.Column(db.String, nullable=False)
        laps = db.Column(db.Integer, nullable=False)
        distance = db.Column(db.Float, nullable=False)
        winner = db.Column(db.String)

    return Race


# Home
@app.route('/')
def home():
    return render_template('home.html')


# Post races to a specific Season by Year
@app.route('/post/races', methods=['POST'])
def post_race():
    key = request.headers.get('X-API-KEY')
    if key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json

    track_id = data.get('track_id')
    name = data.get('name')
    series = data.get('series')
    date = data.get('date')
    laps = data.get('laps')
    distance = data.get('distance')
    winner = data.get('winner')
    year = data.get('year')

    # If not all args are present, return error
    if not year or not track_id or not name or not series or not date:
        return jsonify({'error': 'Invalid Data, Missing Arguments.'}), 400

    try:
        # Create Race table model based on year
        Race = dynamic_races_table(year)

        # Create instance of Race table model
        new_race = Race(track_id=track_id, name=name, series=series, date=date,
                        laps=laps, distance=distance, winner=winner)

        # Add new race to the session and commit to db
        db.session.add(new_race)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({f'error': e}), 400

    else:
        return jsonify({'success': f'Data posted to Races_{year}'}), 201


# Post racetracks
@app.route('/post/tracks', methods=['POST'])
def post_track():
    key = request.headers.get('X-API-KEY')
    if key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json

    name = data.get('name')
    length = data.get('length')
    type = data.get('type')
    state = data.get('state')

    # If not all args are present, return error
    if not name or not length or not type or not state:
        return jsonify({'error': 'Invalid Data, Missing Arguments'}), 400

    try:
        # Create instance of Racetrack table model
        new_track = Racetrack(name=name, length=length, type=type, state=state)

        # Add new race to the session and commit to db
        db.session.add(new_track)
        db.session.commit()

    except Exception as e:
        return jsonify({f'error': e}), 400

    else:
        return jsonify({'success': f'Data posted to Racetracks'}), 201


# Get track names based on State
@app.route('/tracks')
def track_by_state():
    state = request.args.get('state')

    # Get Tracks based on State
    try:
        if state:
            racetracks = Racetrack.query.filter_by(state=state).all()
        else:
            racetracks = Racetrack.query.all()

        # Convert result to a list of track names
        racetracks = [track.name for track in racetracks]

        json = {'tracks': racetracks}

        return jsonify(json)

    except Exception as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500


# Get season schedule based on year
@app.route('/season')
def season():
    series = request.args.get('series')

    # If no year is given, set year to current year
    year = request.args.get('year', datetime.datetime.now().strftime('%Y'))

    # If no valid series is given, default to Cup
    if series == 'xfinity':
        series = 'NASCAR Xfinity Series'
    elif series == 'craftsman':
        series = 'NASCAR Craftsman Truck Series'
    else:
        series = 'NASCAR Cup Series'

    # Get schedule from db
    try:
        metadata = MetaData()
        season_table = Table(f'Races_{year}', metadata, autoload_with=db.engine)
        query = db.session.query(
            Racetrack.name.label('track'),
            season_table.c.name.label('race_name'),
            season_table.c.series,
            season_table.c.date,
            season_table.c.laps,
            season_table.c.distance,
            season_table.c.winner
        ).join(
            Racetrack, season_table.c.track_id == Racetrack.id
        ).filter(
            season_table.c.series == series
        )

        data = query.all()

        json = {series:
                    {f'{year} Season': []}
                }

        for row in data:
            json[series][f'{year} Season'].append({'track': row.track,
                                                   'name': row.race_name,
                                                   'series': row.series,
                                                   'date': row.date,
                                                   'laps': row.laps,
                                                   'distance': row.distance,
                                                   'winner': row.winner})

        return jsonify(json)

    except Exception as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500


@app.route('/winners')
def winners():
    series = request.args.get('series')

    # If no year is given, set year to current year
    year = request.args.get('year', datetime.datetime.now().strftime('%Y'))

    # If no valid series is given, default to Cup
    if series == 'xfinity':
        series = 'NASCAR Xfinity Series'
    elif series == 'craftsman':
        series = 'NASCAR Craftsman Truck Series'
    else:
        series = 'NASCAR Cup Series'

    try:
        # Get winners, number of wins in series for current year
        metadata = MetaData()
        season_table = Table(f'Races_{year}', metadata, autoload_with=db.engine)

        query = db.session.query(
            season_table.c.winner
        ).filter(
            season_table.c.series == series  # Filter by series from the request
        )

        data = query.all()
        winners_dict = defaultdict(int)
        winners_dict = {winner.winner: winners_dict['winner'] + 1 for winner in data}

        # If some races don't have winners yet, delete key None
        if None in winners_dict:
            del winners_dict[None]

        # Sort winners by number of wins, tiebreaker = alphabetize names
        sorted_winners = sorted(winners_dict.items(), key=lambda item: (-item[1], item[0]))

        json = {series:
                    {f'{year} Season':
                         {'winners': {driver: wins for driver, wins in sorted_winners}}
                     }}

        return jsonify(json)

    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
