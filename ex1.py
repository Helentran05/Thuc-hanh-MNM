from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time
options = webdriver.FirefoxOptions()

driver = webdriver.Firefox(
    service=Service(GeckoDriverManager().install()),
    options=options
)

driver.get("https://www.google.com")


# Tạo url
url = "http://pythonscraping.com/pages/javascript/ajaxDemo.html"

# Truy cập
driver.get(url)

# In ra nội dung của trang web
print("Before: ----------------------------------------\n")
print(driver.page_source)

# Tạm dừng khoảng 3 giây
time.sleep(10)

# In lại
print("\n\n\nAfter: ----------------------------------------\n")
print(driver.page_source)

# Đóng browser
driver.quit()
