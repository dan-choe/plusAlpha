import json

data = {'a':['value1', 'value2', 'value3'], 'b':'value4'}

# Write data in json  format
with open('data.json', 'w', encoding='utf-8') as outfile:
    a = json.dump(data, outfile)

with open('data.json', 'r') as f:
    data2 = json.load(f)

print(data2)

# from urllib.request import urlopen
# import json
# u = urlopen('http://search.twitter.com/search.json?q=python&rpp=5')
# resp = json.loads(u.read().decode('utf-8'))
# from pprint import pprint
# pprint(resp)