import pandas as pd
import requests 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time 
import threading

pages_scraped = 0
def scrape_page(start_number, thread_number):
    global pages_scraped
    website = "https://mc.gov.sa/ar/eservices/Pages/Commercial-data.aspx"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--disable-infobars')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(website)
    input_field = driver.find_element('xpath', '//*[@id="ctl00_ctl73_g_7ccc91c8_7990_4f83_84c1_72d098d9838d_ctl00_txtCRName"]')
    input_field.send_keys('البيطرية')
    driver.find_element("xpath","//div[@class='cookieinfo-close']").click()

    driver.execute_script(f"SearchByPaging({1}); return false;")
    df = pd.DataFrame()

    start_time = time.time()
    for n_page in range(start_number, start_number+4):
        panel_bodies= driver.find_elements(By.XPATH, f"//div[@class='panel-body']")
        # wait = WebDriverWait(driver, 10)
        print(f'Thread {thread_number}: scraping page {n_page}')
        # time.sleep(3)
        for i, panel_body in enumerate(panel_bodies, start=1):
            # print('panel body: ', panel_body)
            name_elems = panel_body.find_elements('xpath','./table/tbody/tr/th')
            value_elems = panel_body.find_elements('xpath','./table/tbody/tr/td')

            names = [elem.text for elem in name_elems]
            values = [elem.text for elem in value_elems]
            driver.find_elements(By.CLASS_NAME,"arrow")[i].click() if i < len(panel_bodies) else None

            length = len(df)
            df.loc[length, names] = values

        pages_scraped += 1
        print(f'Thread {thread_number}: scraped page {n_page}')
        print(f'{pages_scraped} pages scraped')
        driver.execute_script(f"SearchByPaging({n_page+1}); return false;")
    df.to_csv(f'{start_number}_to_{start_number+3}.csv', index=False, encoding='utf-8-sig')
    driver.quit()
    
threads = []
urls = []
start_time = time.time()
n_threads = 4
pages_per_thread = 4
start_page = 78
for i in range(start_page, start_page+n_threads*pages_per_thread, pages_per_thread):
    thread = threading.Thread(target=scrape_page, args=(i, len(threads) + 1))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print(f"All scraping threads have completed in {time.time() - start_time}")