import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By


def parse_all_matches(matches):
    data = matches.split('\n')
    print(data)
    for item in range(0, len(data), 3):
        print(data[item-2])
        print(data[item-1])
        print(data[item])



def command_parser(name):
    driver.get('https://www.ligastavok.ru/')
    time.sleep(1)
    driver.find_element(By.ID, f"header-search").click()
    time.sleep(1)
    input_field = driver.find_element(By.CLASS_NAME, 'search-input__input-25c7a1')
    input_field.send_keys(name)
    time.sleep(3)
    teams = driver.find_element(By.CLASS_NAME, 'search-autocomplete-916a6c').text
    if len(teams.replace(' ', '')) == 0:
        print('Команды не обнаружены')
    else:
        print(teams)
        time.sleep(1)
        data = input('введите точное газвание команды')
        input_field.clear()
        input_field.send_keys(data)
        time.sleep(1)
        driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/button').click()
        time.sleep(8)
        matches = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[2]').text
        print(matches)
        if len(matches.replace(' ', '')) == 0:
            print('Нет матчей')
        else:
            parse_all_matches(matches)
        time.sleep(111)


if '__main__' == __name__:
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")  # linux only
    # chrome_options.add_argument("--headless=new")
    driver = uc.Chrome(options=chrome_options)
    command_parser(input('Введите название команды'))

