class User:

    def __init__(self, db_connection):
        self.db = db_connection         

    def create_user(self, name, email, password):
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        return self.db.execute_update(query, (name, email, password))

    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = %s"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None

    def get_user_by_email(self, email):
        query = "SELECT * FROM users WHERE email = %s"
        result = self.db.execute_query(query, (email,))
        return result[0] if result else None

    def get_all_users(self):
        query = "SELECT * FROM users ORDER BY created_at DESC"
        return self.db.execute_query(query)

    def update_user(self, user_id, name=None, email=None, password=None):
        updates = []
        params = []

        if name:
            updates.append("name = %s")
            params.append(name)
        if email:
            updates.append("email = %s")
            params.append(email)
        if age:
            updates.append("password = %s")
            params.append(password)

        if not updates:
            return False

        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        params.append(user_id)

        return self.db.execute_update(query, tuple(params))

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE id = %s"
        return self.db.execute_update(query, (user_id,))
