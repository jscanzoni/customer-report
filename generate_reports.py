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
import locale
import urllib2


mo = int((datetime.datetime.now()-relativedelta(months=1)).strftime("%m"))
yr = int((datetime.datetime.now()-relativedelta(months=1)).strftime("%Y"))

locale.setlocale(locale.LC_ALL, 'en_US')

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
            "Number of Groups",
            "Total Events",
            "Total Notifications",
            "Notifications Delivered",
            "Notifications Responded",
            "Notifications Failed" 
            ]

    data = list()
    html = ""

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
                num_groups = int(n[4])
                num_events = int(n[5])
                total_notifications = int(n[6])
                notifications_delivered = int(n[7])
                notifications_responded =int(n[8])
                notifications_failed  = int(n[9])
                break
            else:
                in_use = 0
                num_groups = 0
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
        licenses_remaining = total_licenses - in_use

        if int(total_licenses) > 0:
            license_utilization = format(float(float(in_use) / float(total_licenses))*float(100), '.2f')
        else:
            license_utilization = 0

        total_standard += standard_users

        data.append([
            m,
            y,
            system_availability,
            target_availability,
            total_licenses,
            full_users,
            standard_users,
            in_use,
            license_utilization,
            licenses_remaining,
            num_groups,
            num_events,
            total_notifications,
            notifications_delivered,
            notifications_responded,
            notifications_failed 
            ])

    directory = './exports'

    if not os.path.exists(directory):
        os.makedirs(directory)

    print '\n'
    print c['customer']
    
    print '--- GENERATING HTML REPORT ---'

    with open ("email_template.html", "r") as htmltemplate:
        html=htmltemplate.read()

    if total_standard == 0:
        license_breakdown = ""
    else:
        license_breakdown = '<br><span style="font-size:9px; font-style:italic; line-height:10px; margin-top:6px; ">'+str(locale.format("%d",data[0][5], grouping=True))+" Full<br>"+str(locale.format("%d",data[0][6], grouping=True))+" Std.</span>"

    #already have this data
    html = html.replace("[[MONTH]]",str((datetime.datetime.now()-relativedelta(months=1)).strftime("%B")))
    html = html.replace("[[YEAR]]",str((datetime.datetime.now()-relativedelta(months=1)).strftime("%Y")))
    html = html.replace("[[COMPANY_NAME]]",str(c['customer']))

     

    html = html.replace("[[TARGET_AVAILABILITY]]",str(data[0][3]))
    html = html.replace("[[SYSTEM_AVAILABILITY]]",str(data[0][2]))

    html = html.replace("[[TOTAL_LICENSES]]",str(locale.format("%d",data[0][4], grouping=True)))
    html = html.replace("[[LICENSE_BREAKDOWN]]",license_breakdown)
    html = html.replace("[[IN_USE]]",str(locale.format("%d",data[0][7], grouping=True)))
    html = html.replace("[[NUM_GROUPS]]",str(locale.format("%d",data[0][10], grouping=True)))
    html = html.replace("[[USER_LAST_MONTH]]",str(locale.format("%d",data[1][7], grouping=True)))
    html = html.replace("[[GROUP_LAST_MONTH]]",str(locale.format("%d",data[1][10], grouping=True)))
    html = html.replace("[[USER_DELTA]]",str(locale.format("%d",data[0][7]-data[1][7], grouping=True)))
    html = html.replace("[[GROUP_DELTA]]",str(locale.format("%d",data[0][10]-data[1][10], grouping=True)))
    html = html.replace("[[LICENSES_REMAINING]]",str(locale.format("%d",data[0][9], grouping=True)))

    for x in range(0, (c['num_months']-1)):

        rep_num = str(x+1)

        html = html.replace("[[NOT"+rep_num+"_MONTH]]",str(datetime.date(1900, int(data[x][0]), 1).strftime('%B')))
        html = html.replace("[[NOT"+rep_num+"_YEAR]]",str(data[x][1]))
        html = html.replace("[[NOT"+rep_num+"_TOTAL]]",str(locale.format("%d",data[x][12], grouping=True)))
        html = html.replace("[[NOT"+rep_num+"_DELIVERED]]",str(locale.format("%d",data[x][13], grouping=True)))
        html = html.replace("[[NOT"+rep_num+"_RESPONDED]]",str(locale.format("%d",data[x][14], grouping=True)))
        html = html.replace("[[NOT"+rep_num+"_FAILED]]",str(locale.format("%d",data[x][15], grouping=True)))

        html = html.replace("[[EV"+rep_num+"_MONTH]]",str(datetime.date(1900, int(data[x][0]), 1).strftime('%B')))
        html = html.replace("[[EV"+rep_num+"_YEAR]]",str(data[x][1]))
        html = html.replace("[[EV"+rep_num+"_EVENTS]]",str(locale.format("%d",data[x][11], grouping=True)))
        html = html.replace("[[EV"+rep_num+"_DELTA]]",str(locale.format("%d",int(data[x][11])-int(data[x+1][11]), grouping=True)))


    text_file = open(directory+"/"+c['report_name']+"-"+str(yr)+"-"+str(mo)+".html", "wb")
    text_file.write(html)
    text_file.close()
    
    print '--- GENERATING CSV REPORT ---'

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
    '''
    print '--- Calling Webhook ---'

    if c['xmatters_form_url']:
        
        payload = {
            'properties': {
                'subject' : 'xMatters - '+str(c['customer'])+' Monthly Report ['+str((datetime.datetime.now()-relativedelta(months=1)).strftime("%B"))+' '+str((datetime.datetime.now()-relativedelta(months=1)).strftime("%Y"))+']',
                'html_body' : html
            }
        }

        req = urllib2.Request(c['xmatters_form_url'])
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, json.dumps(payload))
    '''

    print '--- FINAL DATA ---'

    print (data)