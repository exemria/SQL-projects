import psycopg2
import csv
from datetime import datetime
import os


class Db_books_review:
    
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.con = None
        self.cur = None


    def connect(self):
        self.conn = psycopg2.connect(
        dbname = self.dbname,
        user = self.user,
        password = self.password,
        host = self.host,
        port = self.port
        )
        self.cur = self.conn.cursor()
        
    def disconnect(self): # disconnect database
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    
    def commit(self):
        self.conn.commit()

      
# download all tables from database amazon if exists
def get_table_list(self):
    self.cur.execute("""
        SELECT books, reviews
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    return self.cur.fetchall()

def drop_all_tables(self,tables):
    for table in tables:
        self.cur.execute(f" DROP TABLE IF EXISTS {table[0]} CASCADE")
    self.conn.commit()

def create_table_books(self):
    self.cur.execute('''
        CREATE TABLE "books" (
        "rank" FLOAT,
        "book_title" VARCHAR(255) PRIMARY KEY,
        "book_price" VARCHAR(255),
        "rating" FLOAT,
        "author" VARCHAR(255),
        "year_of_publication" TEXT,
        "genre" VARCHAR(255),
        "url" VARCHAR(255)
    )
    ''')
    self.conn.commit()

def create_table_reviews(self):
    self.cur.execute('''
        CREATE TABLE "reviews" (
            "sno" FLOAT PRIMARY KEY,
            "book_name" VARCHAR(255),
            "review_title" VARCHAR(255),
            "reviewer" VARCHAR(255),
            "rating" FLOAT,
            "review_description" TEXT,
            "js_verified" VARCHAR(255), 
            "date" NUMERIC, 
            "timestamp" VARCHAR(255), 
            "asin" VARCHAR(255),
        FOREIGN KEY ("book_name") REFERENCES "books"("book_title"))
    ''')
    self.conn.commit()
    
    #--FOREIGN KEY ("book_name") REFERENCES "books"("book_title")--
    
#def create_books_dictionary(self):
#    books_data = {}
#
#    try:
#        self.cur.execute("SELECT * FROM books")
#        books_rows = self.cur.fetchall()
#
#        for row in books_rows:
#            book_title = row[1]  # book_title is at index 1
#            books_data[book_title] = row
#
#    except Exception as e:
#        print("Error fetching data from 'books' table:", e)
#
#    return books_data


def insert_data_from_csv(self, file_path1,   file_path2):
    books_data = {}
    with open(file_path1, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            row = [None if cell == '' else cell for cell in row]
            book_title = row[1]
            books_data[book_title] = row
            
            self.cur.execute("""INSERT INTO reviews (Sno, book_name, review_title, reviewer, rating, review_description, js_verified, date, timestamp, ASIN)
                                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", row)
            self.conn.commit()    
            

    with open(file_path2, 'r', encoding='utf-8') as reviews_csv:
        reviews_reader = csv.reader(reviews_csv)
        next(reviews_reader)
        for review_row in reviews_reader:
            # if book_name exists in the books_data, proceed with insertion into reviews table
            book_name = review_row[1] 
            if book_name in books_data:
                # Convert date string to a numeric representation (timestamp)
                date_str = review_row[7]  # Assuming date is at index 7
                try:
                    date_numeric = datetime.strptime(date_str, '%d-%m-%Y').timestamp()
                except ValueError:
                    date_numeric = None
                review_row[7] = date_numeric
                self.cur.execute("""
                    INSERT INTO reviews (Sno, book_name, review_title, reviewer, rating,
                                        review_description, js_verified, date, timestamp, ASIN)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, review_row)
                self.conn.commit()
            else:
                print(f"Book '{book_name}' does not exist in the 'books' table. Skipping insertion into 'reviews'.")
        
                    
            

def main():
    
    try:
        db_action = Db_books_review(
        dbname="amazon",
        user="postgres",
        password="5329",
        host="localhost",
        port="5432"
        )

        db_action.connect()

    except Exception as e:
        print("Error not connected to database", e)
        return 
        
    try:
        tables = db_action.get_table_list()
        db_action.drop_all_tables(tables)
        
    except Exception as e:
        print("Error dropping tables:", e)
        return
    
    try:
        
        db_action.create_table_books()
        db_action.create_table_reviews()
        
    except Exception as e:
        print("Error no table created", e)
        return

    try:
        
        relative_path_to_bookscsv = "resources\Top_100_Trending_Books.csv"
        relative_path_to_reiewscsv = "resources\customer_reviews.csv"
        csv_file_books_path = return_absolute_path(relative_path_to_bookscsv)
        csv_file_reviews_path = return_absolute_path(relative_path_to_reviewscsv)
        
        db_action.insert_data_from_csv(csv_file_books_path, csv_file_reviews_path)

    except Exception as e:
        print("Error inserting data from csv", e)
        return
    
    
    db_action.commit()
    db_action.disconnect()

def return_absolute_path(relative_path):
    
    absolute_path = os.path.dirname(__file__)
    result = os.path.join(absolute_path, relative_path)
    return result

if __name__ == "__main__":
    main()
