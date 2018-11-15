import datetime
import json
from dateutil.relativedelta import relativedelta
from simple_salesforce import Salesforce
from collections import OrderedDict

customers = json.load(open('info.json')) #if auth.json doesn't exist, copy info.json.sample
auth = json.load(open('auth.json')) #if auth.json doesn't exist, copy auth.json.sample

sf = Salesforce(password=auth['salesforce_password'], username=auth['salesforce_username'], security_token=auth['salesforce_token'])

lic = {}
mo = int((datetime.datetime.now()-relativedelta(months=1)).strftime("%m"))
yr = int(datetime.datetime.now().strftime("%Y"))

for c in customers:

    assetinfo = sf.query("SELECT asset.name,assethistory.CreatedDate,assethistory.Field,NewValue,OldValue,asset.full_users__c,asset.standard_users__c, asset.product_new__c, asset.production_url__c,asset.totango_product_account_id__c FROM AssetHistory WHERE asset.totango_product_account_id__c = '"+c['totango_id']+"' and (assethistory.Field = 'Standard_Users__c' or assethistory.Field = 'Full_Users__c') order by CreatedDate DESC")
    
    if assetinfo['totalSize'] == 0:

        assetinfo = sf.query("SELECT name,full_users__c,standard_users__c, product_new__c, production_url__c, totango_product_account_id__c FROM Asset WHERE totango_product_account_id__c = '"+c['totango_id']+"' order by CreatedDate DESC")
        full_users = assetinfo["records"][0]['Full_Users__c']
        standard_users = assetinfo["records"][0]['Standard_Users__c']

        for x in range(0, c['num_months']):
            if (mo-x) > 0:
                m = mo-x
                y = yr
            else:
                m = mo-x+12
                y = yr-1

            #print (str(m)+"-"+str(y))

            lic[str(y)+"-"+str(m)+'-full_users-'+c['totango_id']] = full_users
            lic[str(y)+"-"+str(m)+'-standard_users-'+c['totango_id']] = standard_users
    
    else:

        rec = 0

        full_users = assetinfo["records"][rec]['Asset']['Full_Users__c']
        standard_users = assetinfo["records"][rec]['Asset']['Standard_Users__c']

        for x in range(0, 13):
            if (mo-x) > 0:
                m = mo-x
                y = yr
            else:
                m = mo-x+12
                y = yr-1

            #print (str(m)+"-"+str(y))

            rep_date = datetime.datetime(y,m,1)+relativedelta(day=31)

            try:
                while  rep_date < datetime.datetime.strptime((assetinfo["records"][rec]['CreatedDate'].split('T'))[0],'%Y-%m-%d')+relativedelta(day=31):
                    
                    if assetinfo["records"][rec]['Field'] == 'Full_Users__c':
                        full_users = assetinfo["records"][rec]['OldValue']
                    if assetinfo["records"][rec]['Field'] == 'Standard_Users__c':
                        standard_users = assetinfo["records"][rec]['OldValue']   
                    rec += 1
            except:
                full_users = 0
                standard_users = 0

            lic[str(y)+"-"+str(m)+'-full_users-'+c['totango_id']] = full_users
            lic[str(y)+"-"+str(m)+'-standard_users-'+c['totango_id']] = standard_users

    

#print lic