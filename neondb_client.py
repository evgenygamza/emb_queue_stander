import psycopg2.extras
import psycopg2
from typing import Literal
from user_consts import DB_CONNECTION


class NeonConnect:
    """  # todo
    fetch_select
    add_user
    fetch_user_info
    update_pass
    update_email
    update_position
    delete_user_info

    """
    def __init__(self, dsn, chat_id=None):
        # self.dsn = dsn ??
        self.conn = psycopg2.connect(dsn)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.table = "different_users"
        self.columns = self.get_columns()
        self.id, self.email, self.pswrd, self.position = "chat_id", "email", "passw", "position"
        self.chat_id = chat_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.cur.close()
            self.conn.close()
            # print("Disconnected from the database.")

    def fetch_select(self, query):
        self.cur.execute(query)
        # print(self.cur.description)
        return self.cur.fetchall()

    def get_columns(self):
        columns = self.fetch_select(f"SELECT column_name FROM information_schema.columns \
                                    WHERE table_schema = 'public' AND table_name = '{self.table}';")
        return [column[0] for column in columns]

    def fetch_user_info(self, *cols: Literal["chat_id", "email", "passw", "position"]) -> object:
        if cols:
            return self.fetch_select(f"SELECT {', '.join(cols)} FROM {self.table} WHERE chat_id={self.chat_id};")[0]
        else:
            return self.fetch_select(f"SELECT * FROM {self.table} WHERE chat_id={self.chat_id};")[0]

    def fetch_chat_ids(self):
        result = self.fetch_select(f"SELECT {self.id} FROM {self.table}")
        return [item[0] for item in result]

    def update(self, **columns: Literal["chat_id", "email", "passw", "position"]):
        if not columns:
            print("No columns to update.")
            return self.fetch_user_info()
        try:
            set_clause = ", ".join([f"{key} = '{columns[key]}'" for key in columns.keys() if key in self.columns])
            sql_query = f"UPDATE {self.table} SET {set_clause} WHERE {self.id} = {self.chat_id};"
            self.cur.execute(sql_query)
            self.conn.commit()
            # print("Records updated successfully.")
        except Exception as e:
            print("Error updating records:", e)
        finally:
            return self.fetch_user_info(*columns.keys())

    def check_user_exists(self):
        return self.fetch_select(f"SELECT EXISTS (SELECT 1 FROM {self.table} WHERE {self.id} = {self.chat_id});")[0][0]

    def add_user(self):
        self.cur.execute(f"INSERT INTO {self.table} ({self.id}) VALUES ({self.chat_id});")
        self.conn.commit()
        return self.fetch_user_info()

    def delete_user_info(self):
        self.cur.execute(f"DELETE FROM {self.table} WHERE {self.id} = {self.chat_id}")
        self.conn.commit()


if __name__ == "__main__":
    with NeonConnect(dsn=DB_CONNECTION, chat_id=171819) as db_client:
        result = []
        if not db_client.check_user_exists():
            result.append(db_client.add_user())
        result.append(db_client.update(passw="derparol", email="some@mail.eg", position=9630))
        result.append(db_client.fetch_user_info(db_client.id, db_client.email, db_client.pswrd))
        result.append(db_client.update(position=8841))
        result.append(db_client.fetch_select(f"SELECT * FROM {db_client.table}"))
        result.append(db_client.delete_user_info())
        result.append(db_client.fetch_select(f"SELECT * FROM {db_client.table}"))
        if result:
            for str in result:
                print(f"Query result: {str}")
