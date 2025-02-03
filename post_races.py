import requests
import os

url = 'http://127.0.0.1:5000/post'
headers = {'X-API-KEY': os.getenv('API_KEY')}

app_on = True
while app_on:
    try:
        args = {
            'track_id': int(input('Please Enter a track_id: ')),
            'name': input('Please enter a race name: '),
            'series': input('Please enter a series: '),
            'date': input('Please enter a date: '),
            'winner': input('Would you like to enter a winner? Type y or n: ')
        }

        args['year'] = args['date'][:4]

        if args['winner'] == 'y':
            args['winner'] = input('Please enter a winner: ')
        else:
            args.pop('winner')

        response = requests.post(url, json=args, headers=headers)
        if response.status_code == 201:
            data = response.json()
            print(data)
        else:
            print(f'Failed to post data. Status code: {response.status_code}')

    except KeyboardInterrupt:
        print('\n\nGoodbye.')
        app_on = False
