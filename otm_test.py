from impl.scsl import Database, Table, StringField, IntegerField, ForeignKeyField, ManyToManyField, RelationType

class User(Table):
    id = IntegerField(primary_key=True, unique=True)
    username = StringField(max_length=100)

class Group(Table):
    id = IntegerField(primary_key=True, unique=False)
    host = ForeignKeyField(to=User)
    name = StringField()
    members = ManyToManyField(to=User)

db = Database()
db.add_table(User)
db.add_table(Group)

user1 = User(id=1, username="room owner")
user2 = User(id=2, username="generic user 2")
user3 = User(id=3, username="generic user 3")

db.add_records("User", [user1, user2, user3])

groupchat = Group(
    id=1,
    host=user1,
    name="the group chat",
    members=[user1, user2, user3]
)
db.add_record("Group", groupchat)

tbl = db.get("Group", id=1)
print(tbl.id)
print(tbl.host) # returns pk id
print(tbl.name)
print(tbl.members) # returns pk id's

db.save_to_file("testdata/otm.scdb", "bin")
db.save_to_file("testdata/otm.scsl", "scsl")
db.save_to_file("testdata/otm.json", "json")

print("\nReloading\n")
new_db = Database.load_from_file("testdata/otm.scdb")
loaded_tbl = new_db.get("Group", id=1)
print(loaded_tbl)

print(new_db.get("User", id=1))

new_db.run_admin_panel(save_path="testdata/otm.scdb")