from scdb import Database, Table, StringField, RelationField, RelationType
class User(Table):
    username = StringField(max_length=100)
    password = StringField(max_length=24)

class House(Table):
    name = StringField()
    
    owner = RelationField(to=User, relation_type=RelationType.ONE_TO_ONE, null=False)

db = Database()
db.add_table(User)
db.add_table(House)

db.save_to_file("testdata/schematest.scsl", "scsl")