from scdb import Database, Table, StringField, IntegerField, DateField, TimeField, DateTimeField, ArrayField

from datetime import date, datetime, time

class User(Table):
    id = IntegerField(primary_key=True)
    name = StringField()
    join_date = DateField()
    join_time = TimeField()
    last_login = DateTimeField()
    previous_usernames = ArrayField(str, 5)
    num_list = ArrayField(int, 5)

db = Database()
db.add_table(User)

user = User(
    id=1,
    name="okzyrox",
    join_date=date(2024, 9, 25),
    join_time=time(14, 35, 0),
    last_login=datetime(2024, 9, 25, 14, 35, 0),
    previous_usernames=["okzyrox1", "okzyrox2", "okzyrox3", "okzyrox4"],
    num_list=[1, 2, 3, 4, 5]
)
db.add_record("User", user)

db.save_to_file("testdata/arraytime.scdb", "bin")

newdb = Database.load_from_file("testdata/arraytime.scdb")
newdb.save_to_file("testdata/arraytime.json", "json")
newdb.save_to_file("testdata/arraytime.scsl", "scsl")

print(newdb.get("User", name="okzyrox"))
# join_time=14:35:00
# join_date=2024-09-25

# last_login=2024-09-25 00:00:00
# pain

newdb.run_admin_panel(save_path="testdata/arraytime.scdb")