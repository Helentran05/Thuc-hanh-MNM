from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

s = pd.DataFrame(columns={'Name': [], 'birth': [], 'death': [], 'nationality': []})

driver = webdriver.Chrome()
url = 'https://en.wikipedia.org/wiki/Edvard_Munch'
driver.get(url)

time.sleep(2)
# Name
try :
    name = driver.find_element(By.TAG_NAME, 'h1').text
except:
    name = ''
# Brith
try :
    birth_element = driver.find_element(By.XPATH, '//th[text()="Born"]/following-sibling::td')
    birth = birth_element.text
    birth = re.findall(r"[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}", birth)[0]
except:
    brith = ''
# Death
try :
    death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
    death = death_element.text
    death = re.findall(r"[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}", death)[0]
except:
    death = ''
# Nationality
try:
    nationality_element = driver.find_element(By.XPATH, '//th[text()="Nationality"]/following-sibling::td')
    nationality = nationality_element.text
except:
    nationality = ''

painter = {'Name': name, 'birth': birth, 'death': death, 'nationality': nationality}
painter_df = pd.DataFrame([painter])
d = pd.concat([s, painter_df], ignore_index=True)
print(d)

driver.quit()