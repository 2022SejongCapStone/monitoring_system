from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from threading import Thread
import re

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src import jsonmodule as jm
from src import findfile as ff


options = webdriver.ChromeOptions()
options.add_argument('window-size=1100,900')
options.add_argument('--headless')


class Crawler():

    def __init__(self):
        self.url_list = []
        self.file_thread_list = []
        self.url_thread = None
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.content_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


    def open(self, url=jm.get_secret("STARTURL")):
        self.url_list.append(url)
        self.url_thread = Thread(target=self.findUrlFlow, args=[])
        self.url_thread.setDaemon(True)
        self.url_thread.start()


    def close(self):
        for thd in self.file_thread_list:
            thd.exit()
        self.url_thread.exit()
        return True


    def findUrlFlow(self):
        while True:
            for savedurl in self.url_list:
                if self.isServerExist(savedurl):
                    url_list = self.findUrl()
                    for url in url_list:
                        if url not in self.url_list:
                            url_list.append(url)
                            thd = Thread(target=ff.findFileFlow, args=[url])
                            thd.setDaemon(True)
                            thd.start()
                            self.file_thread_list.append(thd)
                else:
                    self.url_list.remove(savedurl)


    def findUrl(self):
        content_match = []
        try:
            while True:
                for i in range(0, 5):
                    self.driver.find_element(By.XPATH, '/html/body/div/ul[1]/li['+ str(i) +']/div[2]/div[1]/a').click()
                    self.driver.implicitly_wait(3)
                    page = self.driver.find_element(By.XPATH, '/html/body/div')
                    content_match += self.content_re.findall(page.text)
                    self.driver.back()
                    self.driver.implicitly_wait(3)
                self.driver.find_element(By.XPATH, '/html/body/div/ul[2]/li[4]/a').click()
        except NoSuchElementException:
            print("End of posts")
            return content_match
        except Exception as e:
            print("Error in movePageforUrl", e)

    
    def isServerExist(self, savedurl):
        try:
            self.driver.get(savedurl)
            return True
        except WebDriverException:
            print("there is no WebServer")
            return False


    def findFileFlow(url):
        driver = makeFileDriver(url)
        userinfo = jm.get_secret("USERINFO")
        if loginFlow(driver, userinfo, url):
            while True:
                try:
                    for i in range(0, 5):
                        driver.find_element(By.XPATH, '/html/body/div/ul[1]/li['+ str(i) +']/div[2]/div[1]/a').click()
                        driver.implicitly_wait(3)
                        driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div[2]/div/div[1]/form/input[2]').click()
                        #send to client system
                    driver.find_element(By.XPATH, '/html/body/div/ul[2]/li[4]/a').click()
                except NoSuchElementException:
                    print("End of posts")
                    driver.find_element(By.XPATH, '/html/body/nav/div/a').click()
                except Exception as e:
                    print("Error in movePageforUrl", e)
                    return


    def loginFlow(driver, userinfo, url):
        if login(driver, userinfo, url):
            return True
        else:
            if register(driver, userinfo, url):
                if login(driver, userinfo, url):
                    return True
        return False


    def register(driver, userinfo, url):
        try:
            driver.find_element(By.XPATH, "/html/body/div/div/div[2]/p/a").click()
            driver.implicitly_wait(3)
            driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(userinfo["EMAIL"])
            driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(userinfo["ID"])
            driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(userinfo["PW"])
            driver.find_element(By.XPATH, 'password2').send_keys(userinfo["PW"])
            driver.find_element_by_id('submit').click()
            driver.implicitly_wait(3)
            if driver.current_url == url:
                return True
            else:
                print("register failed")
                return False
        except:
            print("error in register function")
            return False


    def login(driver, userinfo, url):
        try:
            driver.find_element(By.XPATH, '//*[@id="navbarNav"]/ul/li/a').click()
            driver.implicitly_wait(3)
            driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(userinfo["EMAIL"])
            driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(userinfo["PW"])
            driver.find_element(By.XPATH, '//*[@id="submit"]').click()
            driver.implicitly_wait(3)
            if driver.current_url == url:
                return True
            else:
                print("login failed")
                return False
        except:
            print("error in login function")
            return False


    def makeFileDriver(url):
        if not os.path.exists('../stock/'+url):
            os.makedirs('../stock/'+url)
        options.add_experimental_option("prefs", {
                                "download.default_directory": "../stock/"+url,
                                "download.prompt_for_download": False,
                                "download.directory_upgrade": True,
                                "safebrowsing.enabled": True
                                })
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver


if __name__ == "__main__":
    url = "http://127.0.0.1:5000/"
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1100,900')
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    driver.find_element(By.XPATH, '//*[@id="navbarNav"]/ul/li/a').click()
    driver.implicitly_wait(3)
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys("yirici2282@hbehs.com")
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys("person123")
    driver.find_element(By.XPATH, '//*[@id="submit"]').click()
    driver.implicitly_wait(3)
    if driver.current_url == url:
        print("login success")
    else:
        print("login failed")