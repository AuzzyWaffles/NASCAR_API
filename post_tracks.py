import requests
import os

url = 'http://127.0.0.1:5000/post/tracks'
headers = {'X-API-KEY': os.getenv('API_KEY')}

# Keep accepting data as long as app is on
app_on = True
while app_on:
    try:
        args = {
            'name': input('Please Enter track name: '),
            'length': float(input('Please enter track length in miles: ')),
            'type': input('Please enter track type: '),
            'state': input('Please enter track state: ')
        }

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
