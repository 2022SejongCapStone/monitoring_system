from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import jsonmodule as jm
import re

class Crawler():

    def __init__(self, url=jm.get_secret("STARTURL")):
        self.url = url
        self.thread_list = []
        userinfo = jm.get_secret("USERINFO") 
        self.id = userinfo["ID"]
        self.email = userinfo["EMAIL"]
        self.pw = userinfo["PW"]
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1100,900')
        options.add_argument('--headless')
        self.driver = webdriver.Chrome("./chromedriver", options=options)
        self.content_re = re.compile('https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')

    
    def open():
        if login():
            findUrl
            
        else:
            if register():
                if login() == False:
                    return False
            else:
                return False
        



    def register(self):
        try:
            self.driver.find_element_by_link_text('회원가입').click()
            self.driver.implicitly_wait(3)
            self.driver.find_element_by_name('email').send_keys(self.email)
            self.driver.find_element_by_name('username').send_keys(self.id)
            self.driver.find_element_by_name('password').send_keys(self.pw)
            self.driver.find_element_by_name('password2').send_keys(self.pw)
            self.driver.find_element_by_id('submit').click()
            self.driver.implicitly_wait(3)
            if self.driver.current_url == self.url:
                return True
            else:
                print("register failed")
                return False
        except:
            print("error in register function in", self.url)
            return False


    def login(self):
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(3)
            driver.find_element(By.XPATH, '//*[@id="navbarNav"]/ul/li/a').click()
            self.driver.implicitly_wait(3)
            driver.find_element(By.XPATH, '//*[@id="email"]').send_keys("yirici2282@hbehs.com")
            driver.find_element(By.XPATH, '//*[@id="password"]').send_keys("person123")
            driver.find_element(By.XPATH, '//*[@id="submit"]').click()
            self.driver.implicitly_wait(3)
            if self.driver.current_url == self.url:
                return True
            else:
                print("login failed")
                return False
        except:
            print("error in login function in", self.url)
            return False


    def findUrl():
        try:
            self.driver.find_element(By.XPATH, '/html/body/div/ul[1]/li[1]/div[2]/div[1]/a').click()
            page = self.driver.find_element(By.XPATH, '/html/body/div')
            content_match = self.content_re.findall(page.text)
            print(content_match.group())
        except:
            print('error in findUrl function in', self.url)
            return False
        

    def findFile():
        try:
            self.driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div[2]/div/div[1]/form/input[2]').click()

        except:
            print('error in findUrl function in', self.url)
            return False

if __name__ == "__main__":
    print(bytes('string'.encode()))
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1100,900')
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("http://20.214.226.173:5000/")
    driver.find_element(By.XPATH, '//*[@id="navbarNav"]/ul/li/a').click()
    driver.implicitly_wait(3)
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys("yirici2282@hbehs.com")
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys("person123")
    driver.find_element(By.XPATH, '//*[@id="submit"]').click()
    driver.implicitly_wait(3)
    driver.find_element(By.XPATH, '/html/body/div/ul[1]/li[1]/div[2]/div[1]/a').click()
    page = driver.find_element(By.XPATH, '/html/body/div')
    driver.implicitly_wait(3)
    content_re = re.compile('https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
    
    print(bytes(page.text.encode()))
    content_match = content_re.findall(page.text)
    print(content_match)
