import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import sqlite3 as sl
import re
from httplib2 import Http
import json
import os

class GoogleChatWebhook():
    def __init__(self,webhook):
        self.webhook = webhook
    def sendAlert(self,message):
        bot_message = {
            'text': message
        }
        message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
        http_obj = Http()
        response = http_obj.request(
            uri=self.webhook,
            method='POST',
            headers=message_headers,
            body=json.dumps(bot_message)
        )
        return response

dbFile = "temp.db"
dbTable = "cars_t"
con = sl.connect(dbFile)
webhook = GoogleChatWebhook(os.environ["TEST_WEBHOOK"])

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

makeModelList = [
    ('proton','saga'),
    ('perodua','bezza')
]
for make,model in makeModelList:
    driver.get(f"https://mytukar.com/my/en/buy/{make}/{model}")
    time.sleep(10)

    locPopup = driver.find_element(by=By.XPATH, value="//h2[contains(text(),'Select Location')]")
    if locPopup:
        driver.find_element(by=By.XPATH, value="//div[7]//button[contains(@class,'AwesomeButton')]/div").click
        time.sleep(10)
        driver.find_element(by=By.XPATH, value="//button[contains(@class,'AwesomeButton')]/span").click
        time.sleep(10)

    for i in range(3):
        action = ActionChains(driver)
        action.move_to_element(driver.find_element(By.XPATH, "//div[@class='copy-right']"))
        time.sleep(10)
        
    carlist = driver.find_elements(by=By.XPATH, value=f"//a[contains(@href,'my/en/cars/{make}/{model}/')]")
    for car in carlist:
        curLink = car.get_attribute("href")
        carDetail = re.search(r'https:\/\/mytukar\.com\/my\/en\/cars\/(?P<make>[^\/]+)\/(?P<model>[^\/]+)\/(?P<title>[^\/]+)\/(?P<id>[^\/]+)',curLink).groupdict()
        with con:
            data = con.execute(f"""
                SELECT *
                FROM {dbTable}
                WHERE make = '{carDetail["make"]}'
                AND model = '{carDetail["model"]}'
                AND title = '{carDetail["title"]}'
                AND id = '{carDetail["id"]}'
            """)
            if len(data.fetchall())==0:
                webhook.sendAlert(f"https://mytukar.com/my/en/cars/{carDetail['make']}/{carDetail['model']}/{carDetail['title']}/{carDetail['id']}")
                con.execute(f"INSERT INTO {dbTable} (id, make, model, title) values('{carDetail['id']}', '{carDetail['make']}', '{carDetail['model']}', '{carDetail['title']}')")
                
driver.close()