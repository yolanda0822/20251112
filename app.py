# app.py
from database import create_table, insert_books
from scraper import scrape_books

def main_menu():
    while True:
        print("\n----- 博客來 LLM 書籍管理系統 -----")
        print("1. 更新書籍資料庫")
        print("2. 查詢書籍")
        print("3. 離開系統")
        print("---------------------------------")
        choice = input("請選擇操作選項 (1-3): ").strip()

        if choice == "1":
            update_database() #執行資料庫更新
        elif choice == "2":
            query_menu() #進入查詢子選單
        elif choice == "3":
            print("感謝使用，系統已退出。")
            break
        else:
            print("無效選項，請重新輸入")

def update_database():
    print("開始從網路爬取最新書籍資料...")
    books = scrape_books()  # 呼叫爬蟲自動搜尋LLM
    if not books:
        print("爬取失敗，請稍後再試。")
        return

    create_table()  # 確保資料表存在，不存在就建立
    new_count = insert_books(books) #將爬到的書籍資料寫入資料庫，回傳新增筆數
    print(f"資料庫更新完成！共爬取 {len(books)} 筆資料，新增了 {new_count} 筆新書記錄。")

def query_menu():
    while True:
        print("\n--- 查詢書籍 ---")
        print("a. 依書名查詢")
        print("b. 依作者查詢")
        print("c. 返回主選單")
        print("---------------")
        choice = input("請選擇查詢方式 (a-c): ").strip().lower() #.lower()小寫化

        if choice == "a":
            keyword = input("請輸入關鍵字: ").strip()
            query_books("title", keyword)
        elif choice == "b":
            keyword = input("請輸入關鍵字: ").strip()
            query_books("author", keyword)
        elif choice == "c":
            return
        else:
            print("無效選項，請重新輸入。")

def query_books(field, keyword):
    import sqlite3
    from database import get_connection #取得資料庫連線

    with get_connection() as conn:
        cursor = conn.cursor()
        sql = f"SELECT * FROM llm_books WHERE {field} LIKE ?" # SQL 模糊查詢
        cursor.execute(sql, (f"%{keyword}%",)) #將關鍵字加上 % 作模糊比對
        results = cursor.fetchall() #取得所有符合的結果

        if not results:
            print("查無資料。")
            return

        for book in results:
            print("\n====================")
            print(f"書名：{book['title']}")
            print(f"作者：{book['author']}")
            print(f"價格：{book['price']}")
        print("====================")

if __name__ == "__main__":
    main_menu() #啟動主選單
