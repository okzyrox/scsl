from impl.scsl import Database, Table, StringField, IntegerField, TableEnum

job_enum = TableEnum(name="Job", values={
    "Accountant": 1,
    "Teacher": 2,
    "Ceo": 3
})

title_enum = TableEnum(name="Title", values={
    "Mr": "mr",
    "Mrs": "mrs",
    "Dr": "dr"
})

class Person(Table):
    name = StringField()
    job = IntegerField()
    title = StringField()

db = Database()

db.add_enum(title_enum)
db.add_enum(job_enum)
db.add_table(Person)

person = Person(name="okzyrox", job=job_enum.values["Ceo"], title=title_enum.values["Mr."])

db.add_record("Person", person)

db.save_to_file("testdata/enums.scdb", "bin")
db.save_to_file("testdata/enums.scsl", "scsl")
db.save_to_file("testdata/enums.json", "json")

loaded_db = Database.load_from_file("testdata/enums.scdb")

loaded_person = loaded_db.get("Person", name="okzyrox")
print(loaded_person)
