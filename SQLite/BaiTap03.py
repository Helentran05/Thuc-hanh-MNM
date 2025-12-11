import sqlite3
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

# CẤU HÌNH SELENIUM
gecko_path = r"C:\Users\LENOVO\OneDrive\Desktop\ma_nguon_mo\SQLite\geckodriver.exe"
options = webdriver.firefox.options.Options()
options.binary_location = r"c:\Program Files\Mozilla Firefox\firefox.exe"
options.headless = False

driver = webdriver.Firefox(service=Service(gecko_path), options=options)
driver.get("https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat")

time.sleep(2)

# CUỘN TRANG + CLICK XEM THÊM
for _ in range(10):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "Xem thêm" in btn.text:
                btn.click()
                time.sleep(5)
                break
    except:
        pass

for _ in range(60):
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
    time.sleep(0.02)

time.sleep(2)

# TẠO DATABASE + TABLE SQLite
db = "longchau_db.sqlite"
conn = sqlite3.connect(db)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sanpham (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_url TEXT UNIQUE,
    product_name TEXT,
    price TEXT,
    original_price TEXT,
    unit TEXT
)
""")
conn.commit()

# TÌM TẤT CẢ SP
buttons = driver.find_elements(By.XPATH, "//button[text()='Chọn mua']")
print("Tổng sản phẩm tìm được:", len(buttons))

# CÀO TỪNG SP + LƯU VÀO SQLite
for index, bt in enumerate(buttons, 1):

    # Thẻ cha chứa thông tin sản phẩm
    div = bt
    for _ in range(3):
        div = div.find_element(By.XPATH, "./..")

    # ===== TÊN SẢN PHẨM =====
    try:
        name = div.find_element(By.TAG_NAME, 'h3').text
    except:
        name = ""

    # ===== GIÁ + UNIT (LẤY TỪ TEXT) =====
    try:
        price_text = div.find_element(By.CLASS_NAME, 'text-blue-5').text
    except:
        price_text = ""

    price = ""
    unit = "Không rõ"

    if '/' in price_text:
    
        price_part, unit_part = price_text.split('/', 1)
        price = price_part.replace('.', '').replace('đ', '').strip()
        unit = unit_part.strip()
    else:
    
        price = price_text.replace('.', '').replace('đ', '').strip()

    # ===== GIÁ GỐC =====
    try:
        original_price_text = div.find_element(By.CLASS_NAME, "line-through").text
        original_price = original_price_text.replace('.', '').replace('đ', '').strip()
    except:
        original_price = price  # nếu không có giá gốc

    # ===== LINK SẢN PHẨM =====
    try:
        link = div.find_element(By.TAG_NAME, 'a').get_attribute('href')
    except:
        continue

    # ===== IN TEST =====
    print(f"[{index}] {name[:30]} | price={price} | unit={unit}")

    # LƯU VÀO SQLite
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO sanpham(product_url, product_name, price, original_price, unit)
        VALUES (?,?,?,?,?)
        """, (link, name, price, original_price, unit))

        conn.commit()

    except Exception as e:
        print("Error:", e)

driver.quit()
# =========================
# Nhóm 1: Kiểm tra chất lượng dữ liệu
# =========================
print("\n--- Nhóm 1: Kiểm tra chất lượng ---")

print("\n1. Trùng lặp product_name:")
for row in cursor.execute("""
    SELECT product_name, COUNT(*) 
    FROM sanpham
    GROUP BY product_name
    HAVING COUNT(*) > 1
"""):
    print(row)

print("\n2. Sản phẩm thiếu giá:")
for row in cursor.execute("""
    SELECT * 
    FROM sanpham
    WHERE price IS NULL OR price = ''
"""):
    print(row)

print("\n3. Giá bán > giá gốc:")
for row in cursor.execute("""
    SELECT * 
    FROM sanpham
    WHERE CAST(price AS INTEGER) > CAST(original_price AS INTEGER)
"""):
    print(row)

print("\n4. Đơn vị tính duy nhất:")
for row in cursor.execute("""
    SELECT DISTINCT unit 
    FROM sanpham
"""):
    print(row)

total = cursor.execute("SELECT COUNT(*) FROM sanpham").fetchone()[0]
print(f"\n5. Tổng số sản phẩm: {total}")

# =========================
# Nhóm 2: Phân tích dữ liệu
# =========================
print("\n--- Nhóm 2: Phân tích dữ liệu ---")

print("\n6. Top 10 sản phẩm giảm giá nhiều nhất:")
for row in cursor.execute("""
    SELECT product_name, original_price, price, 
           (CAST(original_price AS INTEGER) - CAST(price AS INTEGER)) AS discount
    FROM sanpham
    ORDER BY discount DESC
    LIMIT 10
"""):
    print(row)

print("\n7. Sản phẩm đắt nhất:")
for row in cursor.execute("""
    SELECT * 
    FROM sanpham
    ORDER BY CAST(price AS INTEGER) DESC
    LIMIT 1
"""):
    print(row)

print("\n8. Thống kê theo đơn vị:")
for row in cursor.execute("""
    SELECT unit, COUNT(*) 
    FROM sanpham
    GROUP BY unit
"""):
    print(row)

print("\n9. Sản phẩm chứa 'Vitamin C':")
for row in cursor.execute("""
    SELECT * 
    FROM sanpham
    WHERE product_name LIKE '%Vitamin C%'
"""):
    print(row)

print("\n10. Sản phẩm có giá 100.000 - 200.000 VNĐ:")
for row in cursor.execute("""
    SELECT * 
    FROM sanpham
    WHERE CAST(price AS INTEGER) BETWEEN 100000 AND 200000
"""):
    print(row)


# =========================
# Nhóm 3: Các Truy vấn Nâng cao (Tùy chọn)
# =========================
print("\n--- Nhóm 3: Truy vấn nâng cao ---")

# 11. Sắp xếp sản phẩm theo giá bán từ thấp đến cao
print("\n11. Sản phẩm theo giá bán (thấp -> cao):")
for row in cursor.execute("""
    SELECT product_name, price, unit
    FROM sanpham
    WHERE price IS NOT NULL AND price != ''
    ORDER BY CAST(price AS INTEGER) ASC
"""):
    print(row)


# 12. Top 5 sản phẩm có phần trăm giảm giá cao nhất
print("\n12. Top 5 sản phẩm giảm giá (%) cao nhất:")
for row in cursor.execute("""
    SELECT
        product_name,
        original_price,
        price,
        ROUND(
            (CAST(original_price AS REAL) - CAST(price AS REAL)) * 100.0
            / CAST(original_price AS REAL),
            2
        ) AS discount_percent
    FROM sanpham
    WHERE
        original_price IS NOT NULL AND original_price != ''
        AND price IS NOT NULL AND price != ''
        AND CAST(original_price AS REAL) > CAST(price AS REAL)
    ORDER BY discount_percent DESC
    LIMIT 5
"""):
    print(row)


# 13. Xóa bản ghi trùng lặp (giữ 1 bản ghi duy nhất theo product_url)
print("\n13. Xóa bản ghi trùng lặp theo product_url...")
cursor.execute("""
    DELETE FROM sanpham
    WHERE product_id NOT IN (
        SELECT MIN(product_id)
        FROM sanpham
        GROUP BY product_url
    )
""")
conn.commit()
print(" Đã xóa bản ghi trùng lặp.")


# 14. Phân tích nhóm giá
print("\n14. Thống kê sản phẩm theo nhóm giá:")
for row in cursor.execute("""
    SELECT
        CASE
            WHEN CAST(price AS INTEGER) < 50000 THEN 'Dưới 50k'
            WHEN CAST(price AS INTEGER) BETWEEN 50000 AND 100000 THEN '50k - 100k'
            ELSE 'Trên 100k'
        END AS price_group,
        COUNT(*) AS total_products
    FROM sanpham
    WHERE price IS NOT NULL AND price != ''
    GROUP BY price_group
"""):
    print(row)


# 15. Sản phẩm có URL không hợp lệ
print("\n15. Sản phẩm có URL NULL hoặc rỗng:")
for row in cursor.execute("""
    SELECT *
    FROM sanpham
    WHERE product_url IS NULL OR TRIM(product_url) = ''
"""):
    print(row)

conn.close()