import json
import time

import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from wordcloud import WordCloud, STOPWORDS
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import requests
import matplotlib.pyplot as plt
from selenium import webdriver

name = 'Аналитик'


def search(name=None, area=None):
    def getPage(page=0):

        params = {
            'text': f'NAME:{name}',
            'area': area,
            'page': page,
            'per_page': 100,
            'only_with_salary': True
        }
        req = requests.get('https://api.hh.ru/vacancies', params)
        data = req.content.decode()
        req.close()
        return data

    start = np.array([])
    end = np.array([])
    reqs = []
    schedule = {
        'Удаленная работа': 0,
        'Полный день': 0,
        'Гибкий график': 0,
        'Сменный график': 0,
        'Вахтовый метод': 0
    }
    urls = []
    for page in range(0, 500):

        jsObj = json.loads(getPage(page))
        items = jsObj['items']
        for item in items:
            urls.append(item['apply_alternate_url'])
            if item['salary']['from'] is not None and item['salary']['currency'] == 'RUR':
                start = np.append(start, item['salary']['from'])
            if item['salary']['to'] is not None and item['salary']['currency'] == 'RUR':
                end = np.append(end, item['salary']['to'])
            if item['snippet']['requirement'] is not None:
                reqs.append(item['snippet']['requirement'])
            schedule.update({item['schedule']['name']: schedule[item['schedule']['name']] + 1})

        if (jsObj['pages'] - page) <= 1:
            break
    return start, end, reqs, schedule, urls


start, end, reqs, schedule, urls = search(name=name)


def vizualize(reqs, schedule, start, end):
    req_txt = ' '.join(reqs)
    schedule_text = []
    for x in schedule.keys():
        schedule_text.append((x + ' ') * schedule[x])

    schedule_txt = ' '.join(schedule_text)

    stopwords = set(STOPWORDS)
    stopwords.update(["highlighttext"])
    plt.axis("off")
    plt.title(f'Основные обязанности професии {name}')
    wordcloud_req = WordCloud(stopwords=stopwords, max_font_size=50, max_words=50, background_color='white').generate(
        req_txt)
    plt.imshow(wordcloud_req, interpolation='bilinear')
    plt.show()
    plt.axis("off")

    stopwords = set(STOPWORDS)
    stopwords.update(["график"])
    stopwords.update(["работа"])
    stopwords.update(["день"])
    stopwords.update(["метод"])
    plt.title(f'Основные графики работы професии {name}')
    wordcloud_sch = WordCloud(stopwords=stopwords, max_font_size=50, max_words=5, background_color='white',
                              font_step=20).generate(schedule_txt)
    plt.imshow(wordcloud_sch, interpolation='bilinear')

    plt.show()
    plt.title(f'Распределение минимальной и максимальной зарплаты професси {name}')
    plt.hist(start, color='blue', label='min', alpha=0.5)
    plt.hist(end, color='red', label='max', alpha=0.5)
    plt.legend()
    plt.show()



def autoanswering(urls):
    service = Service(executable_path="/home/nikolay/Projects/hh_parser/chromedriver")
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    for url in urls:
        driver.get(url)
        try:
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Войти")))
            driver.find_element(By.LINK_TEXT, "Войти").click()
        except:
            driver.get(url)
            driver.find_element(By.XPATH,'//*[@id="RESPONSE_MODAL_FORM_ID"]/div/div[2]/button').click()
            continue

        wait.until(EC.element_to_be_clickable((By.XPATH,
                                  '//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/div/form/div[4]/button[2]')
        ))
        driver.find_element(By.XPATH,
                                  '//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/div/form/div[4]/button[2]').click()

        wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div/div[1]/div[1]/div[2]/div/form/div[1]/input')))
        wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/form/div[2]/span/input')))
        login = driver.find_element(By.XPATH,'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div/div[1]/div[1]/div[2]/div/form/div[1]/input')
        password = driver.find_element(By.XPATH,'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/form/div[2]/span/input')
        login.clear()
        password.clear()
        login.send_keys('kolya.tanchinec@gmail.com')
        password.send_keys('143625789')

        wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/form/div[4]/div/button[1]')))
        driver.find_element(By.XPATH,'//*[@id="HH-React-Root"]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/form/div[4]/div/button[1]').click()
        time.sleep(10)
        try:
            driver.find_element(By.XPATH, '/html/body/div[12]/div/div[1]/div[5]/div/button[2]')
        except:
            try:
                driver.find_element(By.XPATH,'/html/body/div[13]/div/div[1]/div[5]/div/button[2]')
            except:
                try:
                    driver.find_element(By.XPATH, '/html/body/div[11]/div/div[1]/div[5]/div/button[2]')
                except:
                    try:
                        driver.find_element(By.XPATH, '/html/body/div[10]/div/div[1]/div[5]/div/button[2]')
                    except:
                        continue

autoanswering(urls)
