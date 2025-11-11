from selenium import webdriver #從Selenium套件中匯入控制瀏覽器的模組
from selenium.webdriver.common.by import By #匯入By類別，用來指定要用哪種方式找網頁元素
from selenium.webdriver.common.keys import Keys #是Selenium提供的一個特殊鍵盤按鍵常數集合，可以在輸入框中模擬鍵盤操作
from selenium.webdriver.chrome.options import Options  # Options是 Selenium 為 Chrome 瀏覽器提供的設定類別
from selenium.webdriver.support.ui import WebDriverWait #從Selenium的模組中匯入「等待控制工具」WebDriverWait
from selenium.webdriver.support import expected_conditions as EC #匯入 expected_conditions 模組，讓Selenium可以等到某種條件發生再繼續執行
from bs4 import BeautifulSoup 
import time#內建的時間模組，提供暫停、計時、取得現在時間等功能
import re

def scrape_books():
    #scrape_books函數用來爬取博客來搜尋LLM的所有圖書資料

    options = Options()
    options.add_argument("--headless")  # 無頭模式(不需要開啟瀏覽器視窗)
    options.add_argument("--disable-gpu") #停用GPU加速
    options.add_argument("--no-sandbox")  #避免權限不足導致 Chrome 啟動失敗
    options.add_argument("--start-maximized") #視窗最大化

    driver = webdriver.Chrome(options=options)
     #建立一個可以用來自動操作瀏覽器的物件driver，options=options 把設定的瀏覽器參數套用進去
    wait = WebDriverWait(driver, 20) #建立一個最多等待20秒的等待器

    print("開始從網路爬取最新書籍資料...")

    
    driver.get("https://www.books.com.tw/") #打開博客來首頁
    wait.until(EC.presence_of_element_located((By.ID, "key")))
    #程式會等待，直到網頁出現 id="key"的搜尋框或等20秒後報錯
    #EC.presence_of_element_located 是等待某個元素出現在網頁DOM中

   
    search_box = driver.find_element(By.ID, "key") 
    #找到博客來首頁上那個輸入框 ID = 'key',存到search_box這個變數裡
    search_box.send_keys("LLM")
    #在瀏覽器上的搜尋框裡，自動輸入文字"LLM"
    #.send_keys()：Selenium 的方法，用來模擬鍵盤輸入
    search_box.send_keys(Keys.ENTER)
    #在搜尋框裡按下 Enter，觸發搜尋動作

    # 等待搜尋結果載入
    try:
        wait.until(
            EC.any_of( # Selenium的條件函式，只要其中一個條件成立就算成功
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.searchbook")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-searchbox"))
                #檢查指定的元素是否存在於 DOM 網頁結構中，只要找到其中一種結果容器就繼續往下執行
            )
        )
    except:
        print("搜尋結果未正常載入，可能網路太慢或被網站擋下。")
        driver.quit() #driver.quit()：關閉所有瀏覽器視窗，並結束 WebDriver 會話
        return []

    # 點選「圖書」分類
    try:
        book_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '//label[contains(text(), "圖書")]')))
        #wait.until方法會一直等待，直到指定條件成立，如果 20 秒內條件沒成立，會拋出 TimeoutException
        #EC.element_to_be_clickable()會檢查元素 是否存在且可點擊
        #By.XPATH 是使用 XPath 找元素
        #//label[contains(text(), "圖書")]的意思：找 <label> 標籤且文字內容包含 "圖書"
        
        book_checkbox.click() #找到元素, .click() 是Selenium 方法，用來模擬滑鼠點擊這個元素
        time.sleep(2) #無條件等2秒
    except:
        pass #如果發生任何錯誤，就直接跳過這段程式

    all_books = [] #建立一個空list
    seen_links = set()
    #建立一個空的 集合 (set)，用來存已經爬過的書籍連結，避免同一本書被重複加入 all_books
    current_page = 1 #記錄目前正在爬取的頁數

    while True:
    #建立一個無限迴圈，直到程式內部用 break 跳出為止
        print(f"正在爬取第 {current_page} 頁...")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        #把瀏覽器看到的HTML頁面，交給BeautifulSoup 解析，方便抓書名、作者、價格等資料。
        # html.parser是 Python內建的解析器
        book_blocks = soup.select("div.table-td") or soup.select("li.searchbook-item")
        #先找div標籤且class為table-td的元素，如果找不到就找 li 標籤且 class為searchbook-item的元素

        for b in book_blocks: 
            title_tag = b.select_one("h4 a") #找書名的 <h4> 裡面 <a> 標籤
            author_tags = b.select("p.author a") #找 <p> 標籤且class="author"裡面的 <a> 標籤
            price_blocks = b.select("ul.price li") #找 <ul> 標籤且class="price"裡面的每一個 <li> 標籤

            if not title_tag:
                continue
            #如果沒有抓到書名，就跳過這個書籍，繼續下一個迴圈

            title = title_tag.get_text(strip=True) #取得 <a> 標籤裡的書名，strip=True:去掉前後空白或換行
            link = title_tag.get("href", "").strip() #從 <a> 標籤抓 href屬性(連結)，如果沒有就用空字串 ""
            if link in seen_links:
                continue
            #把抓到的新書連結加入集合，避免重複
            seen_links.add(link) #防止抓到重複的書籍

            authors = ", ".join(a.get_text(strip=True) for a in author_tags) if author_tags else "未知作者"
            #author_tags:所有作者
            #a.get_text(strip=True):把每個作者得文字抓出來，並去掉空格
            # ", ".join():把多個作者用逗號加空格連接成字串
            #if author_tags else "未知作者":沒抓到作者就顯示未知作者

            price = 0
            for p in reversed(price_blocks):
             #reversed代表從最後一個開始抓
                nums = re.findall(r"\d+", p.get_text())
                #用正則表達式找出價格數字
                if nums:
                    price = int(nums[-1]) #將最後一組數字轉整數
                    break

            #打包成字典，再存到all_books
            all_books.append({ 
                "title": title,
                "author": authors,
                "price": price,
                "link": link
            })

        
        try:
            current_page += 1 #頁數+1
            next_btn = driver.find_element(By.LINK_TEXT, str(current_page))
            #By.LINK_TEXT :用超連結文字找元素
            driver.execute_script("arguments[0].click();", next_btn)
            #用瀏覽器的方法點擊下一頁


            wait.until(
                EC.any_of( # Selenium的條件函式，只要其中一個條件成立就算成功
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.searchbook")),
                    #等待頁面出現<div class="searchbook">
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-searchbox"))
                    #等待頁面出現<div class="table-searchbox">
                )
            )
        except:
            break

    driver.quit()#關閉瀏覽器
    print(f"爬取完成，共取得 {len(all_books)} 筆書籍資料。")
    return all_books


if __name__ == "__main__":
    books = scrape_books()
    print(f"\n共爬取 {len(books)} 筆資料\n")
    for b in books:  #顯示
        print(f"{b['title']} - {b['author']} - {b['price']} 元")
