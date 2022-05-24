from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from threading import Thread
from time import sleep
import re
import logging

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src import jsonmodule as jm


logging.basicConfig(filename='../info.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s [%(filename)s]: %(name)s %(funcName)20s - Message: %(message)s')
options = webdriver.ChromeOptions()
options.add_argument('window-size=1100,900')
options.add_argument('--headless')


class Crawler():

    def __init__(self):
        userinfo = jm.get_secret("USERINFO")
        self.id_ = userinfo["ID"]
        self.pw_ = userinfo["PW"]
        self.email_ = userinfo["EMAIL"]
        self.url_list_ = []
        self.file_thread_list_ = []
        self.url_thread_ = None
        self.driver_ = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.content_re_ = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


    def open(self, url=jm.get_secret("STARTURL")):
        self.url_list_.append(url)
        self.url_thread_ = Thread(target=self.findUrlFlow, args=[])
        self.url_thread_.setDaemon(True)
        self.url_thread_.start()
        self.makeFindFileThread(url)


    def close(self):
        # for thd in self.file_thread_list_:
        #     thd.exit()
        # self.url_thread_.exit()
        return True


    def findUrlFlow(self):
        while True:
            url_add = []
            logging.info("findUrlFlow Thread start(self.url_list_) " + str(self.url_list_))
            for savedurl in self.url_list_:
                self.getUrlDriver(savedurl)
                logging.info("savedurl is " + savedurl)
                url_list = self.findUrl()
                logging.info("find all of url(url_list) " + str(url_list))
                for url in url_list:
                    if (url not in self.url_list_) and (self.getUrlDriver(url)):
                        logging.info("append in url list(url_add) " + url)
                        url_add.append(url)
                    else:
                        logging.info("don't append in url list(url_add) " + url)
            for url in url_add:
                self.makeFindFileThread(url)
            self.url_list_ += url_add


    def makeFindFileThread(self, url):
        logging.info("Thread create " + url)
        thd = Thread(target=self.findFileFlow, args=[url])
        thd.setDaemon(True)
        thd.start()
        logging.info("Thread start " + url)
        self.file_thread_list_.append(thd)


    def findUrl(self):
        content_match = []
        try:
            logging.info("Start of findUrl")
            while True:
                for i in range(0, 5):
                    self.driver_.find_element(By.XPATH, '/html/body/div/ul[1]/li['+ str(i+1) +']/div[2]/div[1]/a').click()
                    logging.info("Posts URL " + self.driver_.current_url)
                    self.driver_.implicitly_wait(3)
                    page = self.driver_.find_element(By.XPATH, '/html/body/div')
                    content_match += self.content_re_.findall(page.text)
                    self.driver_.back()
                    self.driver_.implicitly_wait(3)
                self.driver_.find_element(By.XPATH, '/html/body/div/ul[2]/li[4]/a').click()
                logging.info("Page URL " + self.driver_.current_url)
        except NoSuchElementException as e:
            logging.info("End of posts")
            return content_match
        except Exception as e:
            logging.info("Error in movePageforUrl " + e)


    def getUrlDriver(self, savedurl):
        try:
            self.driver_.get(savedurl)
            self.driver_.implicitly_wait(3)
            return True
        except WebDriverException:
            logging.info("there is no WebServer")
            return False


    def findFileFlow(self, url):
        driver = self.makeFileDriver(url)
        driver.get(url)
        if self.loginFlow(driver, url):
            while True:
                try:
                    for i in range(0, 5):
                        driver.find_element(By.XPATH, '/html/body/div/ul[1]/li['+ str(i+1) +']/div[2]/div[1]/a').click()
                        logging.info("Into Posts URL " + driver.current_url)
                        driver.implicitly_wait(3)
                        driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div[2]/div/div[1]/form/input[2]').click()
                        logging.info("Downloads file!")
                        #send to client system
                        driver.back()
                        driver.implicitly_wait(3)
                    driver.find_element(By.XPATH, '/html/body/div/ul[2]/li[4]/a').click()
                    logging.info("Next Page URL " + driver.current_url)
                except NoSuchElementException:
                    logging.info("End of posts")
                    sleep(600)
                    driver.find_element(By.XPATH, '/html/body/nav/div/a').click()
                except Exception as e:
                    logging.info("Error in movePageforUrl " + e)
                    return
        else:
            logging.info("Thread killed")


    def loginFlow(self, driver, url):
        if self.login(driver, url):
            logging.info("login success " + url)
            return True
        else:
            if self.register(driver, url):
                logging.info("register success " + url)
                if self.login(driver, url):
                    logging.info("register and login success " + url)
                    return True
        logging.info("login and register failed... " + url)
        return False


    def register(self, driver, url):
        try:
            driver.find_element(By.XPATH, "/html/body/div/div/div[2]/p/a").click()
            driver.implicitly_wait(3)
            driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(self.email_)
            driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(self.id_)
            driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(self.pw_)
            driver.find_element(By.XPATH, '//*[@id="password2"]').send_keys(self.pw_)
            driver.find_element(By.XPATH, '//*[@id="submit"]').click()
            driver.implicitly_wait(3)
            if driver.current_url == url:
                return True
            else:
                logging.info("register failed")
                return False
        except:
            logging.info("error in register function")
            return False


    def login(self, driver, url):
        try:
            driver.find_element(By.XPATH, '//*[@id="navbarNav"]/ul/li/a').click()
            driver.implicitly_wait(3)
            driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(self.email_)
            driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(self.pw_)
            driver.find_element(By.XPATH, '//*[@id="submit"]').click()
            driver.implicitly_wait(3)
            if driver.current_url == url:
                return True
            else:
                logging.info("login failed")
                return False
        except:
            logging.info("error in login function")
            return False


    def makeFileDriver(self, url):
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]
        if not os.path.exists('../stock/'+url):
            os.makedirs('../stock/'+url)
        options.add_experimental_option("prefs", {
                                "download.default_directory": "../stock/"+url,
                                "download.prompt_for_download": False,
                                "download.directory_upgrade": True,
                                "safebrowsing.enabled": True
                                })
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logging.info("File Driver create")
        return driver


if __name__ == "__main__":
    userinfo = jm.get_secret("USERINFO")
    uid = userinfo["ID"]
    upw = userinfo["PW"]
    email = userinfo["EMAIL"]
    url = "http://127.0.0.1:5000/"
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1100,900')
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    driver.find_element(By.XPATH, '//*[@id="navbarNav"]/ul/li/a').click()
    driver.implicitly_wait(3)
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(email)
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(upw)
    driver.find_element(By.XPATH, '//*[@id="submit"]').click()
    driver.implicitly_wait(3)
    if driver.current_url == url:
        print("login success")
    else:
        print("login failed")
