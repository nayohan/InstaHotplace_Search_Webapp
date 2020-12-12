# -*- coding: utf-8 -*- 
import sys
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver as wd
from bs4 import BeautifulSoup
import time
import datetime
import random
import pymysql
import argparse
from cfg import setting_bigdata as setting

# 해시태그, 아이디, 패쓰워드
usr = ""
pwd = ""
tag_name = ["먹스타그램", "맛스타그램", "맛집", "먹방", "먹스타", "맛있다그램", "맛스타", "맛집탐방", "맛집스타그램"]


class InstagramCrawling:
    def __init__(self, idx):
        self.driver = wd.Chrome(executable_path="./cfg/chromedriver.exe")
        self.tag_idx = idx
        self.hashtag_db = 0
        self.cur = 0
        self.count_non_post = 0

    def login_instagram(self, ):
        self.driver.get('https://www.instagram.com')
        # 게시글 클릭
        self.driver.implicitly_wait(3)

        # 인스타 로그인
        self.driver.find_element_by_name("username").send_keys(usr)
        elem = self.driver.find_element_by_name("password")
        elem.send_keys(pwd)
        elem.submit()

        # 건너뛰기
        self.driver.implicitly_wait(3)
        self.driver.find_element_by_xpath('//button[text()="Not Now"]').click()
        self.driver.implicitly_wait(3)
        self.driver.find_element_by_xpath('//button[text()="Not Now"]').click()

        # 검색
        self.driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[2]/input').send_keys("#" + tag_name[self.tag_idx])      # 검색창
        self.driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[2]/div[4]/div/a[1]/div/div/div[1]/span').click()      # 검색1번

        # 게시글 클릭
        self.driver.implicitly_wait(3)
        self.driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div/div[1]/div[1]/a/div/div[2]').click()

    def login_db(self):
        # db 로그인
        self.hashtag_db = pymysql.connect(
            user=setting.DB_CFG['user'],
            passwd=setting.DB_CFG['passwd'],
            host=setting.DB_CFG['host'],
            db=setting.DB_CFG['db'],
            charset=setting.DB_CFG['charset'])
        self.cur = self.hashtag_db.cursor(pymysql.cursors.DictCursor)

    def send_email(self, crawling_num):
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()      # say Hello
        smtp.starttls()  # TLS 사용시 필요
        smtp.login('email_id', 'pw')

        now = datetime.datetime.now()
        now_datetime = now.strftime('%Y-%m-%d %H:%M:%S')
        msg = MIMEText(usr + " " + str(self.tag_idx) + " num:" + str(crawling_num))
        msg['Subject'] = '[크롤링 오류] ' + now_datetime
        msg['To'] = 'send_email'
        smtp.sendmail('send_email', 'receive_email', msg.as_string())
        smtp.quit()

    def crawling(self):
        # Crawling
        for i in range(0, 3600000):
            print(i)
            time.sleep(random.uniform(3, 4.5))
            # 크롤링
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # 아이디
            id = []
            for wrapper in soup.select("a.sqdOP.yWX7d._8A5w5.ZIAjV"):
                id = wrapper.text
            id = str(id).strip('[]')
            print('아이디: ', id)
            # 장소
            location = []
            for wrapper in soup.select("a.O4GlU"):
                location = wrapper.text
            location = str(location).strip('[]')
            print('장소: ', location)
            # 날짜
            date = []
            for wrapper in soup.select("time.FH9sR.Nzb55"):
                date = wrapper['datetime'][:-5]
                break
            date = str(date).strip('[]').replace("T", " ")
            print('날짜: ', date)

            # 게시글에 있는 해시태그들
            hash_list = []
            for wrapper in soup.find_all("a", "xil3i"):
                hash_list.append(wrapper.text)
            hashtag = str(hash_list).strip('[]').replace("'", "").replace("#", "")
            print('해시태그: ', hashtag)

            # 게시글 # 해시태그 버림 # 댓글 분리
            text = []
            for tag in soup.select("div.C4VMK > span"):
                xil3i = tag.select('a.xil3i')
                for extract_tag in xil3i:
                    extract_tag.extract()
                text.append(tag.getText().strip())
            if text:
                post = text[0]
                del text[0]
            else:
                post = ""
            text = str(text).strip('['']').replace("'", "")
            print('글: ', post)
            print('댓글: ', text)

            # 다음 버튼 누르기
            xpath = '/html/body/div[5]/div[1]/div/div/a[2]'
            try:
                self.driver.find_element_by_xpath(xpath).click()   # 글 안나올때있어서 변경
            except:
                self.send_email(i)
                sys.exit(1)
            if self.count_non_post == 10:
                self.send_email(i)
                sys.exit(1)
            # db 추가
            if not date:
                self.count_non_post += 1
            else:
                try:    
                        self.cur.execute("replace into HashTag (id, location, date, hashtag, post, comment) values (%s, %s, %s, %s, %s, %s)", (id, location, date, hashtag, post, text))
                        self.hashtag_db.commit()
                        self.count_non_post = 0
                except:
                        self.send_email(i)

        # db 닫기
        self.hashtag_db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", type=int, required=True, default=0, help="Hashtag idx")
    args = parser.parse_args()

    Crwal = InstagramCrawling(args.l)
    Crwal.login_instagram()
    Crwal.login_db()
    Crwal.crawling()
