import sqlite3
import csv
import json
import threading


class DB:
    _local_data = threading.local()

    def __init__(self, db_name):
        if not hasattr(DB._local_data, 'conn'):
            DB._local_data.conn = sqlite3.connect(
                db_name, check_same_thread=False)
        self.conn = DB._local_data.conn
        self.cursor = self.conn.cursor()

    def execute_sql(self, sql, params=None):
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def table_exists(self, table_name):
        try:
            self.cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            return self.cursor.fetchone() is not None
        except Exception:
            return False

    def is_table_empty(self, table_name):
        if not self.table_exists(table_name):
            print(f"{table_name} 表不存在")
            return None
        self.cursor.execute(f"SELECT 1 FROM '{table_name}' LIMIT 1")
        return self.cursor.fetchone() is None

    def create_table(self, table_name):
        try:
            sql = """
                CREATE TABLE "{}" (
                    "md5_id"            TEXT,
                    "chapter_id"               INTEGER,
                    "chapter_title" TEXT,
                    "chapter_url"   TEXT,
                    "chapter_sum"  TEXT
                    )
                    """.format(table_name)
            self.execute_sql(sql)
        except sqlite3.OperationalError:
            print(f"{table_name} 表已存在")

    def delete_table(self, table_name):
        sql = f"DROP TABLE {table_name}"
        self.execute_sql(sql)

    def insert_data(self, table_name, md5_id, id, chapter_title, chapter_url, chapter_sum):
        sql = f"INSERT INTO '{
            table_name}' (md5_id, chapter_id, chapter_title, chapter_url, chapter_sum) VALUES (?, ?, ?, ?, ?)"
        params = (md5_id, id, chapter_title, chapter_url, chapter_sum)
        self.execute_sql(sql, params)

    def select_data(self, table_name, column_name, value):
        try:
            sql = f"SELECT * FROM {table_name} WHERE {column_name} = ?"
            params = (value,)
            self.execute_sql(sql, params)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def update_data(self, table_name, column_name, new_value, condition_column, condition_value):
        if not self.table_exists(table_name):
            return
        sql = f"UPDATE '{table_name}' SET {
            column_name} = ? WHERE {condition_column} = ?"
        params = (new_value, condition_value)
        self.execute_sql(sql, params)

    def get_all_data(self, table_name):
        sql = f"SELECT * FROM '{table_name}'"
        self.execute_sql(sql)
        result = self.cursor.fetchall()
        return result

    def delete_data(self, table_name, value=None, query=None):
        if value is not None and query is None:
            sql = f"DELETE FROM {table_name} WHERE {query} = ?"
            params = (value,)
            self.execute_sql(sql, params)

    def export_data(self, table_name, file_path, file_type):
        if not self.table_exists(table_name):
            return
        data = self.get_all_data(table_name)
        if file_type == "csv":
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(
                    ['md5_id', 'chapter_id', 'chapter_title', 'chapter_url', 'chapter_sum'])
                for row in data:
                    csv_writer.writerow(row)
        elif file_type == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=4))
        else:
            print("文件类型不支持")

    @staticmethod
    def close_all_connections():
        # 关闭所有线程的数据库连接
        if hasattr(DB._local_data, 'conn'):
            DB._local_data.conn.close()
            del DB._local_data.conn


if __name__ == '__main__':
    db = DB("cache.db")
    db.create_table("变成女孩子在惊悚世界不想再社恐")
    # db.insert_data("变成女孩子在惊悚世界不想再社恐", 0, "11", "22", None)
    # print(db.table_exists("变成女孩子在惊悚世界不想再社恐"))
