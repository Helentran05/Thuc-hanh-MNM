import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re
import os

######################################################
## I. Cấu hình và Chuẩn bị
######################################################

DB_FILE = 'Painters_Data.db'
TABLE_NAME = 'painters_info'
all_links = []

# Xóa DB cũ nếu tồn tại
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Đã xóa file DB cũ: {DB_FILE}")

# Kết nối SQLite và tạo bảng
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    name TEXT PRIMARY KEY,
    birth TEXT,
    death TEXT,
    nationality TEXT
);
"""
cursor.execute(create_table_sql)
conn.commit()
print(f"Đã kết nối và chuẩn bị bảng '{TABLE_NAME}' trong '{DB_FILE}'.")

def safe_quit_driver(driver):
    try:
        if driver:
            driver.quit()
    except:
        pass

######################################################
## II. Lấy Đường dẫn (URLs) - FIXED VERSION
######################################################

print("\n--- Bắt đầu Lấy Đường dẫn ---")

for i in range(70, 71):  # Chỉ lấy chữ F
    driver = None
    try:
        driver = webdriver.Chrome()
        url = f"https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22{chr(i)}%22"
        print(f"Đang truy cập: {url}")
        driver.get(url)
        time.sleep(3)

        # CÁCH MỚI: Tìm thẻ <ul> chứa class="mw-parser-output"
        # Hoặc tìm tất cả <ul> và in ra để debug
        ul_tags = driver.find_elements(By.TAG_NAME, "ul")
        print(f"Tổng số thẻ <ul> tìm thấy: {len(ul_tags)}")
        
        # Thử tìm <ul> có chứa nhiều <li> nhất (đó thường là danh sách họa sĩ)
        max_li_count = 0
        best_ul = None
        
        for idx, ul in enumerate(ul_tags):
            li_tags = ul.find_elements(By.TAG_NAME, "li")
            li_count = len(li_tags)
            
            # In ra để debug - xem ul nào có nhiều li nhất
            if li_count > 10:  # Chỉ xem những ul có trên 10 items
                print(f"  ul[{idx}]: {li_count} items")
                
            if li_count > max_li_count:
                max_li_count = li_count
                best_ul = ul
        
        if best_ul:
            print(f"\n✅ Đã chọn <ul> có {max_li_count} items")
            li_tags = best_ul.find_elements(By.TAG_NAME, "li")
            
            # Lấy links từ các <li>
            for li in li_tags:
                try:
                    link = li.find_element(By.TAG_NAME, "a").get_attribute("href")
                    # Chỉ lấy link Wikipedia về người (không lấy category, file, v.v.)
                    if link and "/wiki/" in link and ":" not in link.split("/wiki/")[1]:
                        all_links.append(link)
                        print(f"  + Link: {link}")
                except:
                    pass
        else:
            print("❌ Không tìm thấy <ul> phù hợp")

    except Exception as e:
        print(f"Lỗi khi lấy links cho ký tự {chr(i)}: {e}")
    finally:
        safe_quit_driver(driver)

print(f"\n✅ Hoàn tất lấy đường dẫn. Tổng cộng {len(all_links)} links đã tìm thấy.")

######################################################
## III. Lấy thông tin & LƯU TRỮ
######################################################

print("\n--- Bắt đầu Cào và Lưu Trữ ---")
count = 0
success_count = 0

for link in all_links:
    if count >=10:
        break
    count += 1
    
    print(f"\n[{count}] Đang xử lý: {link}")
    driver = None
    
    try:
        driver = webdriver.Chrome()
        driver.get(link)
        time.sleep(2)

        # Lấy tên
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""
            
        print(f"  Tên: {name}")
        
        # Lấy ngày sinh
        try:
            birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            birth = birth_element.text
            birth_match = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', birth)
            birth = birth_match[0] if birth_match else ""
        except:
            birth = ""
            
        print(f"  Sinh: {birth}")
            
        # Lấy ngày mất
        try:
            death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
            death = death_element.text
            death_match = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', death)
            death = death_match[0] if death_match else ""
        except:
            death = ""
            
        print(f"  Mất: {death}")
            
        # Lấy quốc tịch
        try:
            nationality_element = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
            nationality = nationality_element.text.split('\n')[0]
        except:
            nationality = ""
            
        print(f"  Quốc tịch: {nationality}")

        safe_quit_driver(driver)
        
        # Lưu vào DB
        if name:  # Chỉ lưu nếu có tên
            insert_sql = f"INSERT OR IGNORE INTO {TABLE_NAME} (name, birth, death, nationality) VALUES (?, ?, ?, ?);"
            cursor.execute(insert_sql, (name, birth, death, nationality))
            conn.commit()
            success_count += 1
            print(f"  ✅ Đã lưu thành công!")
        else:
            print(f"  ⚠️ Bỏ qua - không có tên")

    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        safe_quit_driver(driver)

print(f"\n✅ Hoàn tất! Đã lưu {success_count}/{count} họa sĩ.")

######################################################
## IV. Truy vấn SQL
######################################################

print("\n" + "="*50)
print("TRUY VẤN DỮ LIỆU")
print("="*50)

#A. Yêu Cầu Thống Kê và Toàn Cục
1#. Đếm tổng số họa sĩ đã được lưu trữ trong bảng.
sql1 = f"SELECT COUNT(*) AS total_painters FROM {TABLE_NAME};"
df1 = pd.read_sql_query(sql1, conn)
print("\n1. Tổng số họa sĩ:")
print(df1)

#2. Hiển thị 5 dòng dữ liệu đầu tiên để kiểm tra cấu trúc và nội dung bảng.
sql2 = f"SELECT * FROM {TABLE_NAME} LIMIT 5;"
df2 = pd.read_sql_query(sql2, conn)
print("\n2. 5 dòng đầu tiên:")
print(df2)

#3. Liệt kê danh sách các quốc tịch duy nhất có trong tập dữ liệu.
sql3 = f"SELECT DISTINCT nationality FROM {TABLE_NAME} WHERE nationality != '';"
df3 = pd.read_sql_query(sql3, conn)
print("\n3. Các quốc tịch:")
print(df3)

#B. Yêu Cầu Lọc và Tìm Kiếm
#4. Tìm và hiển thị tên của các họa sĩ có tên bắt đầu bằng ký tự 'F'.
sql4 = f"SELECT name FROM {TABLE_NAME} WHERE name LIKE 'F%';"
df4 = pd.read_sql_query(sql4, conn)
print("\n4. Họa sĩ có tên bắt đầu bằng 'F':")
print(df4)
#5. Tìm và hiển thị tên và quốc tịch của những họa sĩ có quốc tịch chứa từ khóa 'French' (ví dụ: French, French-American).
sql5 = f"SELECT name, nationality FROM {TABLE_NAME} WHERE nationality LIKE '%French%';"
df5 = pd.read_sql_query(sql5, conn)
print("\n5. Họa sĩ có quốc tịch chứa 'French':")
print(df5)
#6. Hiển thị tên của các họa sĩ không có thông tin quốc tịch (hoặc để trống, hoặc NULL).
sql6 = f"SELECT name FROM {TABLE_NAME} WHERE nationality = '' OR nationality IS NULL;"
df6 = pd.read_sql_query(sql6, conn)
print("\n6. Họa sĩ không có thông tin quốc tịch:")
print(df6)
#7. Tìm và hiển thị tên của những họa sĩ có cả thông tin ngày sinh và ngày mất (không rỗng).
sql7 = f"SELECT name FROM {TABLE_NAME} WHERE birth != '' AND death != '' AND birth IS NOT NULL AND death IS NOT NULL;"
df7 = pd.read_sql_query(sql7, conn)
print("\n7. Họa sĩ có đầy đủ thông tin sinh-mất:")
print(df7)
#8. Hiển thị tất cả thông tin của họa sĩ có tên chứa từ khóa '%Fales%' (ví dụ: George Fales Baker).
sql8 = f"SELECT * FROM {TABLE_NAME} WHERE name LIKE '%Fales%';"
df8 = pd.read_sql_query(sql8, conn)
print("\n8. Họa sĩ có tên chứa 'Fales':")
print(df8)

#C. Yêu Cầu Nhóm và Sắp Xếp
#9. Sắp xếp và hiển thị tên của tất cả họa sĩ theo thứ tự bảng chữ cái (A-Z).
sql9 = f"SELECT name FROM {TABLE_NAME} ORDER BY name ASC;"
df9 = pd.read_sql_query(sql9, conn)
print("\n9. Danh sách họa sĩ theo thứ tự A-Z:")
print(df9)
#10. Nhóm và đếm số lượng họa sĩ theo từng quốc tịch.
sql10 = f"SELECT nationality, COUNT(*) AS count FROM {TABLE_NAME} WHERE nationality != '' GROUP BY nationality ORDER BY count DESC;"
df10 = pd.read_sql_query(sql10, conn)
print("\n10. Thống kê họa sĩ theo quốc tịch:")
print(df10)

# Đóng kết nối
conn.close()
print("\n Đã đóng kết nối cơ sở dữ liệu.")
