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
import socket
import pickle

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src import jsonmodule as jm
from src import database as db
from src import directory as dt
from src import AdditiveElgamal as ae
from src import compare as cp
from scripts import analysis as al


logging.basicConfig(filename='../info.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s [%(filename)s]: %(name)s %(funcName)20s - Message: %(message)s')
options = webdriver.ChromeOptions()
options.add_argument('window-size=1100,900')
options.add_argument('--headless')


class Crawler():

    def __init__(self):
        userinfo = jm.get_secret("USERINFO")
        self.host_ = jm.get_secret("HOST")
        self.port_ = jm.get_secret("PORT")
        self.id_ = userinfo["ID"]
        self.pw_ = userinfo["PW"]
        self.email_ = userinfo["EMAIL"]
        self.url_list_ = []
        self.file_thread_list_ = []
        self.url_thread_ = None
        self.driver_ = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.content_re_ = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.serversocket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clientlist_ = []
        self.clientlistforjoin_ = []


    def open(self, url=jm.get_secret("STARTURL")):
        key = jm.get_secret("KEY")
        self.privkey_ = ae.construct_additive((key['P'], key['G'], key['Y'], key['X']))
        self.server_thread = Thread(target=self.serverSocketFlow, args=[])
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        sleep(5)
        self.url_list_.append(url)
        self.url_thread_ = Thread(target=self.findUrlFlow, args=[])
        self.url_thread_.setDaemon(True)
        self.url_thread_.start()
        self.makeFindFileThread(url)


    def close(self):
        # for thd in self.file_thread_list_:
        #     thd.exit()
        # self.url_thread_.exit()
        # self.serversocket_.close()
        # for client in self.clientlist_:
        #     client.close()
        return True


    def serverSocketFlow(self):
        key = jm.get_secret("KEY")
        self.serversocket_.bind((self.host_, self.port_))
        self.serversocket_.listen()
        while True:
            clientsocket, addr = self.serversocket_.accept()
            publickey = {}
            publickey["P"] = key["P"]
            publickey["G"] = key["G"]
            publickey["Y"] = key["Y"]
            clientsocket.sendall(pickle.dumps(publickey))
            # key exchange
            self.clientlist_.append(clientsocket)


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
        dir_path = ""
        if url.startswith("http://"):
            dir_path = url[7:]
        elif url.startswith("https://"):
            dir_path = url[8:]
        driver = self.makeFileDriver(url)
        driver.get(url)
        if self.loginFlow(driver, url):
            while True:
                dbcontrol = db.URLDataBase(url)
                try:
                    for i in range(0, 10):
                        driver.find_element(By.XPATH, '/html/body/div/ul[1]/li['+ str(i+1) +']/div[2]/div[1]/a').click()
                        logging.info("Into Posts URL " + driver.current_url)
                        driver.implicitly_wait(3)
                        if dbcontrol.isDataExist(driver.current_url):
                            continue
                        if not driver.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div/div[1]/div[2]').text.endswith('.c'):
                            driver.back()
                            driver.implicitly_wait(3)
                            logging.info("Not .c file")
                            continue
                        driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div[2]/div/div[1]/form/input[2]').click()
                        sleep(5)
                        logging.info("Downloads file! " + driver.current_url)
                        dbcontrol.insert(driver.current_url)
                        # Server to Client
                        extractedFragments = al.analysis("stock/"+dir_path+'content/')
                        self.makeServerThread(extractedFragments, driver.current_url)
                        for clntthd in self.clientlistforjoin_:
                            clntthd.join()
                        # Server to Client
                        driver.back()
                        driver.implicitly_wait(3)
                        logging.info("DELETE directory! ")
                        dt.deleteDir('stock/'+dir_path+'content/')
                        dt.deleteDir("../system/")
                        logging.info("CREATE directory! ")
                        dt.makeDir('stock/'+dir_path+'content/')
                        dt.makeDir("../system/")
                    driver.find_element(By.XPATH, '/html/body/div/ul[2]/li[4]/a').click()
                    logging.info("Next Page URL " + driver.current_url)
                    dbcontrol.dump()
                except NoSuchElementException:
                    logging.info("End of posts")
                    dbcontrol.close()
                    sleep(60)
                    driver.find_element(By.XPATH, '/html/body/nav/div/a').click()
                except Exception as e:
                    logging.info("Error in movePageforUrl " + str(e))
                    dbcontrol.close()
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
        dt.deleteDir("stock/")
        dt.deleteDir("../system/")
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]
        dt.makeDir("stock/"+url+'content/')
        dt.makeDir("../system/")
        options.add_experimental_option("prefs", {
                                "download.default_directory": "stock/"+url+"content/",
                                "download.prompt_for_download": False,
                                "download.directory_upgrade": True,
                                "safebrowsing.enabled": True
                                })
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logging.info("File Driver create")
        return driver


    def makeServerThread(self, data, url):
        logging.info("Server thread create")
        for client in self.clientlist_:
            thd = Thread(target=self.interactFlow, args=[client, data, url])
            thd.setDaemon(True)
            thd.start()
            self.clientlistforjoin_.append(thd)
        logging.info("Server thread start")
    

    def interactFlow(self, client, extractedfragments, url):
        try:
            logging.info(extractedfragments)
            count = 0
            for k, v in extractedfragments.items():
                for i in v:
                    count += 1
            client.sendall(str(count).encode().ljust(10, b'A'))
            sleep(1)
            cfid_list = []
            for k, v in extractedfragments.items():
                for i in v:
                    packet = {}
                    cfid_list.append(i.id)
                    packet[k] = cp.encrypt_simhash(self.privkey_, i.simhash)
                    client.sendall(pickle.dumps(packet))
                    sleep(1)
                    client.sendall("EndofPacket".encode())
                    sleep(1)
            data = []
            while True:
                packet = client.recv(1500)
                if b"EndofPacket" == packet:
                    # data.append(packet[:packet.find(b"EndofPacket")])
                    break
                data.append(packet)
            enc_HD_dict_list = pickle.loads(b"".join(data))

            for cfid, enc_HD_dict in zip(cfid_list, enc_HD_dict_list):
                for clnt_cfid, enc_HD in enc_HD_dict.items():
                    sim = self.privkey_._decrypt(enc_HD)
                    logging.info("Sim Value: "+str(sim))
                    if sim <= 14:
                        client.sendall(b"YYYYYYYYYY")
                        sleep(1)
                        reportdict = {}
                        for k, v in extractedfragments.items():
                            for i in v:
                                if i.id == cfid:
                                    reportdict["serv_file"] = i.startline
                                    reportdict["serv_startline"] = i.file
                                    reportdict["serv_endline"] = i.endline
                                    reportdict["serv_content"] = i.content
                                    reportdict["clnt_cfid"] = clnt_cfid
                                    reportdict["darkweb_url"] = url
                        client.sendall(pickle.dumps(reportdict))
                        sleep(1)
                        client.sendall(b"EndofPacket")
                        sleep(1)
                        return "Email sending"
                    else:
                        client.sendall(b"NNNNNNNNNN")
                        sleep(1)
                        return "Not Real File"
        except Exception as e:
            print("Error", e)
            self.clientlist_.remove(client)
            client.close()
            return "End of socket"
            

if __name__ == "__main__":
    userinfo = jm.get_secret("USERINFO")
    uid = userinfo["ID"]
    upw = userinfo["PW"]
    email = userinfo["EMAIL"]
    url = "http://20.214.226.173:5000/post_reply/2"
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1100,900')
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    if not driver.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div/div[1]/div[2]').text.endswith('.c'):
        driver.back()
        driver.implicitly_wait(3)
        print("Not .c file")

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
