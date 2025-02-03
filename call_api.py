import requests

url = 'http://127.0.0.1:5000/race'

date = input('Please Enter a Date YYYY-MM-DD:\n')
time = input('\nPlease Enter a Time HH:MM:SS:\n')

response = requests.get(f'{url}?date={date}&time={time}')
data = response.json()

print(data['race']['date']['message'])
print(data['race']['time']['message'])
