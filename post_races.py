import requests
import os

url = 'http://127.0.0.1:5000/post/races'
headers = {'X-API-KEY': os.getenv('API_KEY')}

# Keep accepting data as long as app is on
app_on = True
while app_on:
    try:
        args = {
            'track_id': int(input('Please Enter a track_id: ')),
            'name': input('Please enter a race name: '),
            'series': input('Please enter a series: '),
            'date': input('Please enter a date: '),
            'laps': int(input('Please enter how many laps: ')),
            'distance': float(input('Please enter distance: ')),
            'winner': input('Would you like to enter a winner? Type y or n: ')
        }

        args['year'] = args['date'][:4]

        # Delete winner if no winner is given
        if args['winner'] == 'y':
            args['winner'] = input('Please enter a winner: ')
        else:
            args.pop('winner')

        # Delete empty data
        for key, val in args.items():
            if val == '':
                args.pop(key)

        # Call API
        response = requests.post(url, json=args, headers=headers)
        if response.status_code == 201:
            data = response.json()
            print(data)
        else:
            print(f'Failed to post data. Status code: {response.status_code}')

    # If app is turned off
    except KeyboardInterrupt:
        print('\n\nGoodbye.')
        app_on = False
