class Post:

    def __init__(self, db_connection):
        self.db = db_connection

    def create_post(self, content, user_id):
        query = "INSERT INTO posts (content, user_id) VALUES (%s, %s)"
        return self.db.execute_update(query, (content, user_id))

    def get_post_by_id(self, post_id):
        query = "SELECT * FROM posts WHERE id = %s"
        result = self.db.execute_query(query, (post_id,))
        return result[0] if result else None

    def get_all_posts(self):
        query = "SELECT * FROM posts INNER JOIN users ON posts.user_id = users.id ORDER BY posts.created_at DESC"
        return self.db.execute_query(query)

    def update_post(self, post_id, content):
        query = "UPDATE posts SET content = %s WHERE id = %s"
        return self.db.execute_update(query, (content, post_id))
    
    def delete_post(self, post_id):
        query = "DELETE FROM posts WHERE id = %s"
        return self.db.execute_update(query, (post_id,))
