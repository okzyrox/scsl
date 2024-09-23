from impl.scsl import Database, Table, StringField, IntegerField

db = Database()

class User(Table):
    id = IntegerField()
    name = StringField()
    age = IntegerField()

db.add_table(User)

db.add_record("User", User(id=1, name="Alice", age=25))
db.add_record("User", User(id=2, name="Bob", age=30))

print(db.get("User", id=1)) # if only 1 matching object exists, then that object is returned
# otherwise, a list is returned

print(db.all("User")) # Returns a list always
print(db.get("User", name="Bob"))

## Output:
# > User: id = 1, name = Alice, age = 25
# > [User(id=1, name=Alice, age=25), User(id=2, name=Bob, age=30)]
# > User: id = 2, name = Bob, age = 30