from selenium import webdriver
from selenium.webdriver.common.by import By
import time

#Khởi tạo webdriver
driver = webdriver.Chrome()

#Mở trang
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22"
driver.get(url)

# Đợi một chút để trang tải
time.sleep(2)

#đợi một chút để trang tải
ul_tags = driver.find_elements(By.TAG_NAME, "ul")
print(len(ul_tags))

# chọn thể ul thứ 21
ul_painters = ul_tags[20] #List start with index=0

#lấy ra tất cả cá theer <li> thuoc ul_painters
li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

#tạo danh sách các url
links = [tag.find_element(By.TAG_NAME, "a").get_attribute("href")for tag in li_tags]

#tạo sanh sách các url
titles = [tag.find_element(By.TAG_NAME, "a").get_attribute("title")for tag in li_tags]

#in ra url
for link in links:
    print(link)

#in ra title
for title in titles:
    print(title)

#Dong webdriver
driver.quit()
