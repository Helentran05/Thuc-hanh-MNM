from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

#Tạo dataframe rỗng

all_links = []
d = pd.DataFrame({'name': [], 'birth': [], 'nationality': []})

#Lấy danh sách link painters

for i in range(70, 71):  # 70 = 'F', 71 = 'G'
    driver = webdriver.Chrome()
    url = f"https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22{chr(i)}%22"

    try:
        driver.get(url)
        time.sleep(2)

        #Lấy tất cả link họa sĩ trong danh sách
        li_tags = driver.find_elements(By.CSS_SELECTOR, "div.div-col ul li a")

        links = [tag.get_attribute("href") for tag in li_tags]
        all_links.extend(links)

    except Exception as e:
        print("Error!", e)

    driver.quit()

#Lấy thông tin từng họa sĩ

count = 0
for link in all_links:
    if count >= 5:  # chỉ lấy 5 link để test
        break
    count += 1

    print("Đang lấy:", link)

    try:
        driver = webdriver.Chrome()
        driver.get(link)
        time.sleep(2)

        try:
            name = driver.find_element(By.ID, "firstHeading").text
        except:
            name = ""

        try:
            birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            birth = birth_element.text.strip()
        except:
            birth = ""

        try:
            nationality_element = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
            nationality = nationality_element.text.strip()
        except:
            nationality = ""

        painter = {'name': name, 'birth': birth, 'nationality': nationality}
        d = pd.concat([d, pd.DataFrame([painter])], ignore_index=True)

        driver.quit()

    except Exception as e:
        print("Lỗi:", e)
        continue

#Xuất Excel

print(d)
file_name = "Painter.xlsx"
d.to_excel(file_name, index=False)
print("Đã lưu file", file_name)
