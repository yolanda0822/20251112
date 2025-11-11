import sqlite3  # 引用標準模組sqlite3

DB_File = "books.db"  # 資料庫檔案名稱

#定義一個名為 get_connection 的函數，會回傳一個 sqlite3.Connection 型別的資料庫連線物件
def get_connection() -> sqlite3.Connection:
  
    conn = sqlite3.connect(DB_File) #連線資料庫
    conn.row_factory = sqlite3.Row  # 設定 row_factor，查詢結果的每一列會變成一個類似字典的物件，可以同時用索引和欄位名稱來存取資料
    return conn #回傳

def create_table() -> None: #None不會回傳任何的值
    # 建立 llm_books 資料表（若不存在）
    # id      INTEGER PRIMARY KEY AUTOINCREMENT   書籍編號，自動累加
    # title   TEXT NOT NULL UNIQUE                書名，不可為空且唯一
    # author  TEXT                                作者
    # price   INTEGER                             價格
    # link    TEXT                                書籍連結
    with get_connection() as conn:  # 使用with確保連線會自動關閉
        cursor = conn.cursor()      # 建立 cursor 物件

        # 建立資料表
        cursor.execute("""          
            CREATE TABLE IF NOT EXISTS llm_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                author TEXT,
                price INTEGER,
                link TEXT
            )
        """)
        conn.commit()  # 提交變更

def insert_books(books: list[dict]) -> int:
    # 將書籍列表插入資料表，若書名已存在則忽略
    # books(list[dict]): 書籍資訊列表，每個 dict 包含 title, author, price, link
    # 回傳：int(新增的書籍數量)
    new_count = 0  # 記錄新增書籍數量
    try:
        with get_connection() as conn: #使用with確保連線會自動關閉
            cursor = conn.cursor()  # 建立 cursor 物件
        

            for book in books:

                # 使用 INSERT OR IGNORE 避免重複書名產生錯誤
                cursor.execute(
                    "INSERT OR IGNORE INTO llm_books (title, author, price, link) VALUES (?, ?, ?, ?)",
                    (book["title"], book.get("author"), book.get("price"), book.get("link"))
                )
                new_count += cursor.rowcount  # 本次新增的筆數（0 或 1）
                #.rowcount	告訴最近一次透過這個游標執行 INSERT (新增)、UPDATE (更新)、或 DELETE (刪除)等SQL指令時，有多少筆資料被成功影響

            conn.commit()  # 提交所有新增操作
    except sqlite3.Error as e:
        # 捕捉所有與SQLite資料庫操作相關的錯誤，將錯誤訊息印出方便除錯
        print(f"[資料庫錯誤] 無法寫入資料：{e}")

    return new_count
