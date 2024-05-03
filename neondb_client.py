import psycopg2.extras
from user_consts import DB_CONNECTION
import psycopg2


class NeonConnect:
    """
    fetch_select
    add_user
    fetch_user_info
    update_pass
    update_email
    update_position
    delete_user_info

    """
    def __init__(self, dsn, chat_id):
        # self.dsn = dsn ??
        self.conn = psycopg2.connect(dsn)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.table = "different_users"
        self.id, self.email, self.pswrd, self.position = "chat_id", "email", "passw", "position"
        self.chat_id = chat_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.cur.close()
            self.conn.close()
            # print("Disconnected from the database.")

    def fetch_select(self, query: str):
        self.cur.execute(query)
        # print(self.cur.description)
        return self.cur.fetchall()
    
    def add_user(self):
        self.cur.execute(f"INSERT INTO {self.table} ({self.id}) VALUES ({self.chat_id});")
        self.conn.commit()
        return self.fetch_select(f"SELECT * FROM {self.table} WHERE chat_id={self.chat_id};")[0][0]

    def fetch_user_info(self):
        return self.fetch_select(f"SELECT * FROM {self.table} WHERE chat_id={self.chat_id};")[0]
    
    def update(self, **columns):
        if not columns:
            print("No columns to update.")
            return
        try:
            set_clause = ", ".join([f"{key} = %s" for key in columns.keys()])
            values = list(columns.values())
            sql_query = f"UPDATE {self.table} SET {set_clause}, "
            self.cur.execute(sql_query, values)
            self.conn.commit()
            print("Records updated successfully.")
        except Exception as e:
            print("Error updating records:", e)
        finally:
            return self.fetch_select(f"SELECT * FROM {self.table} WHERE chat_id={self.chat_id};")[0][0]


    def update_pass(self, new_pass: str):
        self.cur.execute(f"UPDATE {self.table}\
                           SET {self.pswrd} = '{new_pass}'\
                           WHERE {self.id} = {self.chat_id};")
        self.conn.commit()
        return self.fetch_select(f"SELECT {self.pswrd} FROM {self.table} WHERE chat_id={self.chat_id};")[0][0]

    def update_email(self, new_email: str):
        self.cur.execute(f"UPDATE {self.table}\
                           SET {self.email} = '{new_email}'\
                           WHERE {self.id} = {self.chat_id};")
        self.conn.commit()
        return self.fetch_select(f"SELECT {self.email} FROM {self.table} WHERE chat_id={self.chat_id};")[0][0]
    
    def update_position(self, new_pos: int):
        self.cur.execute(f"UPDATE {self.table}\
                           SET {self.position} = '{new_pos}'\
                           WHERE {self.id} = {self.chat_id};")
        self.conn.commit()
        return self.fetch_select(f"SELECT {self.position} FROM {self.table} WHERE chat_id={self.chat_id};")[0][0]

    def delete_user_info(self):
        self.cur.execute(f"DELETE FROM {self.table} WHERE {self.id} = {self.chat_id}")
        self.conn.commit()


if __name__ == "__main__":
    with NeonConnect(dsn=DB_CONNECTION, chat_id=171819) as db_client:
        result = []
        result.append(db_client.add_user())
        result.append(db_client.fetch_user_info())
        result.append(db_client.update_pass("derparol"))
        result.append(db_client.update_email("some@mail.eg"))
        result.append(db_client.update_position(9630))
        result.append(db_client.update(position=8841))
        result.append(db_client.fetch_select(f"SELECT * FROM {db_client.table}"))
        result.append(db_client.delete_user_info())
        result.append(db_client.fetch_select(f"SELECT * FROM {db_client.table}"))
        if result:
            for str in result:
                print(f"Query result: {str}")
