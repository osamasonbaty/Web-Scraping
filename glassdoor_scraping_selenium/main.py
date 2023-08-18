from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import numpy as np
import re
import tkinter as tk

def toggle_password_visibility():
    if show_password_var.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")

def save_inputs():
    global email, password, job_title, location
    email = email_var.get()
    password = password_var.get()
    job_title = job_title_var.get()
    location = location_var.get()

    # Close the GUI window after saving
    app.destroy()

# Create the main application window
app = tk.Tk()
app.title("Input Form")

# Create and place input labels and entry fields
tk.Label(app, text="Email:").pack()
email_var = tk.StringVar()
tk.Entry(app, textvariable=email_var).pack()

tk.Label(app, text="Password:").pack()
password_var = tk.StringVar()
password_entry = tk.Entry(app, textvariable=password_var, show="*")
password_entry.pack()

# Checkbox for showing/hiding the password
show_password_var = tk.BooleanVar()
show_password_checkbox = tk.Checkbutton(app, text="Show Password", variable=show_password_var, command=toggle_password_visibility)
show_password_checkbox.pack()

tk.Label(app, text="Job Title:").pack()
job_title_var = tk.StringVar()
tk.Entry(app, textvariable=job_title_var).pack()

tk.Label(app, text="Location:").pack()
location_var = tk.StringVar()
tk.Entry(app, textvariable=location_var).pack()

# Create and place the 'Save' button
tk.Button(app, text="Save", command=save_inputs).pack()

# Start the GUI event loop
app.mainloop()
driver = webdriver.Chrome()
driver.get('https://www.glassdoor.com/')
assert "Glassdoor" in driver.title
elem = driver.find_element(By.ID, "inlineUserEmail")
elem.clear()
elem.send_keys(email)
elem.send_keys(Keys.RETURN)
time.sleep(5)
elem = driver.find_element(By.ID, "inlineUserPassword")
elem.clear()
elem.send_keys(password)
elem.send_keys(Keys.RETURN)
try:
    element_present = EC.presence_of_element_located((By.ID, "sc.keyword"))
    WebDriverWait(driver, 5).until(element_present)
except TimeoutException:
    print ("Timed out waiting for page to load")

elem = driver.find_element(By.ID, "sc.keyword")
elem.clear()
elem.send_keys(job_title)

elem = driver.find_element(By.ID, "sc.location")
elem.send_keys(Keys.CONTROL + "a")
elem.send_keys(Keys.DELETE)
elem.send_keys(location)
elem.send_keys(Keys.RETURN)
time.sleep(1)
#press see all jobs
driver.find_element(By.XPATH, "//div[@class='mt-std d-flex justify-content-center']").click()
time.sleep(5)
#find number of pages
driver.get('https://www.glassdoor.com/Job/egypt-data-analyst-jobs-SRCH_IL.0,5_IN69_KO6,18.htm?includeNoSalaryJobs=true')
if not n_pages:
    n_pages = driver.find_element(By.XPATH, "//div[@class='paginationFooter']").text
    n_pages = int(re.findall(r'\d', n_pages)[1])

res = []
for i in range(n_pages):
    class_name = "//div[@class='css-3x5mv1']" if i > 0 else "//div[@class='job-search-3x5mv1']"

    #find job posts
    elems = driver.find_elements(By.XPATH, class_name)
    print(f'I\'m on loop {i} and the is len(elems): {len(elems)}')

    for elem in elems:
        info = elem.text.split('\n')
        info.insert(-1, 'Website') if 'Easy Apply' not in info else None

        #add job link
        info.append(elem.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'))

        #remove salary if exists as it's not mentioned most of the time
        info.pop(3) if len(info) > 6 else None
        res.append(info[:6])

    #click next page
    driver.find_element(By.XPATH, "//button[@class='nextButton job-search-opoz2d e13qs2072']").click()
    print(f'I finished loop {i} and pressed next {i+1} times')
    time.sleep(1)

print(f'{len(res)} results found')
result = pd.DataFrame(res, columns=['company', 'position', 'location', 'applying_method', 'day_posted', 'link'])

result['rating'] = result.company.apply(lambda x: ''.join(re.findall(r'\d\.\d', x)))
result.rating = result.rating.replace('', np.nan, regex=True).astype(float)

result.company.replace(' ★', '', regex=True, inplace=True)
result.company = result['company'].str.replace('\d\.\d', '', regex=True)

result.day_posted = result.day_posted.apply(lambda x: ''.join(re.findall(r'\d+', x))).astype(int)
result.sort_values(['day_posted', 'rating'], ascending=[True, False], inplace=True)
result.to_csv('result.csv', index=False)
