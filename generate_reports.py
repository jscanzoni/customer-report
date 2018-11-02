from totango_prompt import notifications

print "--- Pulling from Salesforce ---"

from salesforce_pull import lic

print "--- Pulling from Pingdom ---"

from pingdom_pull import up

print "--- Generating Reports ---"


from dateutil.relativedelta import relativedelta

import datetime
import json
import csv
import os

mo = int((datetime.datetime.now()-relativedelta(months=1)).strftime("%m"))
yr = int(datetime.datetime.now().strftime("%Y"))

customers = json.load(open('info.json')) #if auth.json doesn't exist, copy info.json.sample

for c in customers:
    
    header = [
            "Month",
            "Year",
            "System Availability",
            "Target Availability",
            "Total Licenses",
            "Full Users",
            "Standard Users",
            "Licenses In Use",
            "License Utilization",
            "Licenses Remaining",
            "Total Events",
            "Total Notifications",
            "Notifications Delivered",
            "Notifications Responded",
            "Notifications Failed" 
            ]

    data = list()
    #data.append(header)
    total_standard = 0

    for x in range(0, c['num_months']):

        if (mo-x) > 0:
            m = mo-x
            y = yr
        else:
            m = mo-x+12
            y = yr-1

        for n in notifications:
            #print [int(n[0]),int(n[1]),n[2]] , [m,y,c['totango_id']] 
            if int(n[0]) == m and int(n[1]) == y and str(n[2]) == str(c['totango_id']):
                in_use = int(n[3])
                num_events = int(n[4])
                total_notifications = int(n[5])
                notifications_delivered = int(n[6])
                notifications_responded =int(n[7])
                notifications_failed  = int(n[8])
                break
            else:
                in_use = 0
                num_events = 0
                total_notifications = 0
                notifications_delivered = 0
                notifications_responded = 0
                notifications_failed  = 0

        system_availability = up[str(y)+"-"+str(m)+'-full_users-'+c['totango_id']]
        target_availability = c['availability']
        full_users = int(lic[str(y)+"-"+str(m)+'-full_users-'+c['totango_id']])
        standard_users = int(lic[str(y)+"-"+str(m)+'-standard_users-'+c['totango_id']])
        total_licenses = int(full_users) + int(standard_users)
        license_utilization = format(float(float(in_use) / float(total_licenses))*float(100), '.2f')
        licenses_remaining = total_licenses - in_use

        total_standard += standard_users

        data.append([
            m,
            yr,
            system_availability,
            target_availability,
            total_licenses,
            full_users,
            standard_users,
            in_use,
            license_utilization,
            licenses_remaining,
            num_events,
            total_notifications,
            notifications_delivered,
            notifications_responded,
            notifications_failed 
            ])

    print c['customer']
    print (data)

    directory = './exports'

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(directory+"/"+c['report_name']+"-"+str(yr)+"-"+str(mo)+".csv", 'wb') as myfile:
        #wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, lineterminator='\n')
        #wr.writerow(data)
        writer = csv.writer(myfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        
        if total_standard == 0: #remove license breakdown if everyone is a full user
            header.pop(6)
            header.pop(5)
        writer.writerow(header)
        for item in data:
            #Write item to outcsv
            if total_standard == 0: #remove license breakdown if everyone is a full user
                item.pop(6)
                item.pop(5)
            writer.writerow(item)