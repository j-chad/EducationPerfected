from random import choice
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from fuzzywuzzy import process as fuzzy_process

RANDOM_SPLIT = True


def create_driver():
    return webdriver.Chrome()


def main():
    driver = create_driver()
    driver.get('https://www.educationperfect.com/app/#/login')
    cached_url = driver.current_url
    while True:
        url = driver.current_url
        if not url == cached_url:
            source = driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
            if is_vulnerable(driver, soup, url):
                driver.execute_script("document.body.style.pointerEvents = 'none';")
                data = scan(soup)
                driver.execute_script("document.body.style.pointerEvents = '';")
                #driver.find_element_by_css_selector('.infinity').click()
                driver.find_element_by_id('start-button-main').click()
                question_loop(data, driver)
            cached_url = url


def is_vulnerable(driver, soup, url):
    if (soup.find(id='list-icon')) and ('/list-starter' in url):
        with open('injections/vuln.js', 'r') as script:
            driver.execute_script(script.read())
        while True:
            try:
                WebDriverWait(driver, 60).until(EC.alert_is_present())
            except TimeoutException:
                return False
            else:
                alert = driver.switch_to.alert
                if alert.text == 'Activated':
                    alert.accept()
                    return True
                elif alert.text == 'Cancelling':
                    alert.accept()
                    return False
                else:
                    continue


def scan(soup):
    questions = soup.select('.stats-item > .h-group')
    data = {}
    for i in questions:
        question, answer = i.find_all(class_='question-label')
        #Transpose To Text
        question, answer = map(lambda x: x.text.strip(), (question, answer))
        for o in question.split(';'):
            o = o.strip()
            if o != '':
                data[o] = answer
    print(data)
    return data


def question_loop(data, driver):
    prev_question = None
    while True:
        question = driver.find_element_by_id('question-text')
        question = question.text
        print(question)
        if question != prev_question:
            print(question, data.get(question))
            answer = data.get(question)
            if answer is None:
                answer = data[fuzzy_process.extractOne(question, list(data.keys()))[0]]
            if ';' in answer and RANDOM_SPLIT:
                answer = choice(answer.split(';'))
            elif ',' in answer and RANDOM_SPLIT:
                answer = choice(answer.split(';'))
            answer_box = driver.find_element_by_css_selector('#answer-text-container > #answer-text')
            answer_box.send_keys(answer)
            prev_question = question
        else:
            try:
                error_modal = driver.find_element_by_css_selector('tr.incorrect>#users-answer-field')
            except NoSuchElementException:
                print('No Modal')
            else:
                data[prev_question] = error_modal.text
                print("REFINED: {} = {}".format(prev_question, error_modal.text))
                driver.find_element_by_css_selector('#continue-button').click()


if __name__ == '__main__':
    main()
