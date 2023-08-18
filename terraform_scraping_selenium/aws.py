from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode
chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration for headless mode

links = ['https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket',
         'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_acl',
         'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_cors_configuration',
         'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_intelligent_tiering_configuration']

h2_id = 'argument-reference'

# Install chrome driver and run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager(version='114.0.5735.90').install()), options=chrome_options)

for link in links:
    res = []
    driver.get(link)
    time.sleep(3)
    # Find the <h2> element with the specified id
    h2_element = driver.find_element(By.ID, h2_id)

    # Now, use the relative XPath to find the <ul> element that follows the <h2> element
    # This XPath selects the first <ul> element after the <h2> element
    ul_element = h2_element.find_element(By.XPATH, './following-sibling::ul[1]')

    # Once you have the <ul> element, you can extract the bullet points (if any)
    # For example, to get the text content of each <li> element within the <ul>:
    bullet_points = ul_element.find_elements(By.TAG_NAME, 'li')
    for bullet_point in bullet_points:
        res.append(bullet_point.text.split(' - '))
    result = pd.DataFrame(res, columns = ['argument_name', 'argument_description'])
    name = link.split('/')[-1]
    result.to_csv(f'{name}.csv', index=False)