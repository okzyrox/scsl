from impl.scsl import Database, Table, StringField, IntegerField, ForeignKeyField, ManyToManyField, RelationType

class User(Table):
    id = IntegerField(primary_key=True, unique=True)
    username = StringField(max_length=100)
    password = StringField(max_length=24)

class Group(Table):
    id = IntegerField(primary_key=True, unique=False)
    name = StringField()
    members = ManyToManyField(to=User)

db = Database()
db.add_table(User)
db.add_table(Group)

user1 = User(id=1, username="user1", password="pass1")
user2 = User(id=2, username="user2", password="pass2")
db.add_record("User", user1)
db.add_record("User", user2)

group = Group(id=1, name="group1", members=[user1, user2])
db.add_record("Group", group)

# To get the contents of the many to many field table
# since the name is done automatically and not defined by the db creator
print(db.get_related_table_record("Group", 1, "User"))

db.save_to_file("testdata/mtm.scdb", "bin")
db.save_to_file("testdata/mtm.scsl", "scsl")

print("reloading")
new_db = Database.load_from_file("testdata/mtm.scdb")

print(new_db.get("Group", id=1))
print(new_db.get_related_table_record("Group", 1, "User"))