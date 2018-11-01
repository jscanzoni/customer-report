from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.relativedelta import relativedelta

import os
import time
import json
import datetime

up = {}
mo = int((datetime.datetime.now()-relativedelta(months=1)).strftime("%m"))
yr = int(datetime.datetime.now().strftime("%Y"))

customers = json.load(open('info.json')) #if auth.json doesn't exist, copy info.json.sample
auth = json.load(open('auth.json')) #if auth.json doesn't exist, copy auth.json.sample

usernameStr = auth['pingdom_username']
passwordStr = auth['pingdom_password']

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

chrome_driver = os.getcwd() +"/chromedriver"

browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

browser.get(('https://my.pingdom.com/'))


# fill in username and hit the next button
username = browser.find_element_by_name('email')
username.send_keys(usernameStr)
password = browser.find_element_by_name('password')
password.send_keys(passwordStr)
nextButton = browser.find_elements_by_xpath("//*[contains(text(), 'Log in')]")
nextButton[0].click() 


dashboardTitle = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH,"//*[contains(text(), 'Dashboard')]")))


for c in customers:
    customer = c['pingdom_id']

    for x in range(0, c['num_months']):
        if (mo-x) > 0:
            m = mo-x
            y = yr
        else:
            m = mo-x+12
            y = yr-1
        
        if m == 12:
            end_month = 1
            end_year = y + 1
        else:
            end_month = m + 1
            end_year = y
            
        start = str(int(time.mktime(time.strptime(str(y)+'-'+str(m)+'-01 07:00:00', '%Y-%m-%d %H:%M:%S'))) - time.altzone)
        end = str(int(time.mktime(time.strptime(str(end_year)+'-'+str(end_month)+'-01 06:59:59', '%Y-%m-%d %H:%M:%S'))) - time.altzone)

        browser.get(('https://my.pingdom.com/reports/uptime#daterange='+start+'-'+end+'&tab=uptime_tab&check='+str(customer)))

        downtime = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"pd-main-chart-uptime")))

        time.sleep(1)

        while downtime.text is None or downtime.text == "":
            time.sleep(1)

        up[str(y)+"-"+str(m)+'-full_users-'+c['totango_id']] = (downtime.text).replace('%','')

browser.quit()

#print up

#print downtime.getAttribute("value")

#<h2 class="pd-main-chart-downtime">None</h2>


#reportsButton = browser.find_elements_by_xpath("//*[contains(text(), 'Reports')]")
#reportsButton[0].click()

#uptimeButton = WebDriverWait(browser, 10).until(
#    EC.presence_of_element_located((By.CLASS_NAME.XPATH,"//*[contains(text(), 'Uptime')]")))
#uptimeButton.click()

# wait for transition then continue to fill items
#password = WebDriverWait(browser, 10).until(
#    EC.presence_of_element_located((By.ID, 'Passwd')))
#password.send_keys(passwordStr)
 
#signInButton = browser.find_element_by_id('signIn')
#signInButton.click()


#https://my.pingdom.com/reports/uptime#daterange=7days&tab=uptime_tab&check=1017132