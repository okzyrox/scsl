from impl.scsl import Database, Table, StringField, IntegerField

# 1k users
# db = Database()
# class User(Table):
#     id = IntegerField()
#     name = StringField()

# db.add_table(User)
# for i in range(1, 1001): # 1000 users
#     db.add_record("User", User(id=i, name=f"User {i}"))

# db.save_to_file("testdata/1kusers.scdb", "bin") # 40kb

# new_db = Database.load_from_file("testdata/1kusers.scdb")

# for i in range(1, 1001):
#     print(new_db.get("User", id=i))


# 100k users

# db = Database()

# class User(Table):
#     id = IntegerField()
#     name = StringField()

# db.add_table(User)
# for i in range(1, 100001): # 100000 users
#     print("at:", i)
#     db.add_record("User", User(id=i, name=f"User {i}"))

# db.save_to_file("testdata/100kusers.scdb", "bin") # 4mb, took abt 2 mins


#1k posts short posts

# import random
# import string

# db = Database()

# class Post(Table):
#     id = IntegerField()
#     title = StringField()
#     content = StringField()

# db.add_table(Post)
# for i in range(1, 1001): # 1000 posts, 25 chars long content
#     db.add_record("Post", Post(id=i, title=f"Post {i}", content=''.join(random.choices(string.ascii_uppercase + string.digits, k=25))))

# db.save_to_file("testdata/1kposts.scdb", "bin") # 81kb
# took: less than a second

# 1k posts long posts

# import random 
# import string

# db = Database()

# class Post(Table):
#     id = IntegerField()
#     title = StringField()
#     content = StringField()

# db.add_table(Post)
# for i in range(1, 1001): # 1000 posts, 250 chars long content
#     db.add_record("Post", Post(id=i, title=f"Post {i}", content=''.join(random.choices(string.ascii_uppercase + string.digits, k=250))))

# db.save_to_file("testdata/1klongposts.scdb", "bin") # 300kb
# took: abt 1s.