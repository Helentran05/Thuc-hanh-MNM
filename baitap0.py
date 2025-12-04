from selenium import webdriver
from selenium.webdriver.common.by import By
import time

#Tạo 1 driver de bắt đầu điều khiển
driver = webdriver.Chrome()

#Mở một trang web
driver.get("https://gomotungkinh.com/")
#đợi 5s
time.sleep(5)

try:
    while True:
        driver.find_element(By.ID, "bonk").click()
        #tam dung 1s
        time.sleep(1)
except:
    driver.quit()
