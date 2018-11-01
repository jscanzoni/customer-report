import os
import json
import csv

auth = json.load(open('auth.json')) #if auth.json doesn't exist, copy auth.json.sample

os.system('clear')

customers = json.load(open('info.json')) #if auth.json doesn't exist, copy info.json.sample

customer_in = ''

for c in customers:

    customer_in = '\n"' + c['totango_id'] + '",' + customer_in

customer_in = customer_in[:-1]

print(auth['query_instructions']+'\n') #parameterized and moved value to auth.json for security reasons

print(auth['query'].replace('@@@',customer_in)) #parameterized and moved value to auth.json for security reasons

raw_input('\nPress Enter once you have the results...')

os.system('clear')

print ("Please paste results and then hit enter twice:")

lines = []
while True:
    line = raw_input()
    if line:
        if not line.startswith( '---' ) and not (line.strip()).startswith('mon'):
            lines.append((line.replace(' ','')).replace('|',','))
    else:
        break

x = csv.reader((lines))
notifications = list(x)

#print (data)
#print (piperows)