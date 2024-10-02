from impl.scsl import Database, Table, TableEnum, StringField, IntegerField, RelationField, RelationType
class User(Table):
    id = IntegerField(primary_key=True, unique=False)
    username = StringField(max_length=100)
    password = StringField(max_length=24)

class House(Table):
    id = IntegerField(primary_key=True, unique=False)
    name = StringField()
    
    owner = RelationField(to=User, relation_type=RelationType.ONE_TO_ONE, null=False)

user_enum = TableEnum(name="Title", values={
    "Mr": 1,
    "Mrs": 2,
    "Dr": 3
})

db = Database()
db.add_table(User)
db.add_table(House)
db.add_enum(user_enum)

for i in range(10):
    db.add_record("User", User(id=i, username=f"user {i}", password = "i am a password"))

for i in range(2):
    db.add_record("House", House(id=i, name=f"house {i}", owner=db.get("User", username=f"user {i}")))

db.save_to_file("testdata/paneldb.scdb", "bin")
db.run_admin_panel(
    port = 8080,
    debug = True,
    save_path = "testdata/paneldb.scdb"
)