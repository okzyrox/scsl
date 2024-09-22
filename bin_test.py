from impl.scsl import Table, StringField, Database
from cryptography.fernet import Fernet

class User(Table):
    username = StringField(max_length=100)
    password = StringField(max_length=24)





action = input("action (bin/encrypt): ")
if action == "bin":
    print("Bin test (no encrypt)")
    db = Database()
    db.add_table(User)
    me = User(username = "okzyrox", password = "hi")
    db.add_record("User", me)

    for i in range(0, 10):
        person = User(username = "testuser" + str(i), password = "test")
        db.add_record("User", person)

    print("Saving:")
    db.save_to_file("testdata/users.scdb", "bin")
    print("")
    print("Loading")
    loaded_db = db.load_from_file("testdata/users.scdb")

    for tableName, values in loaded_db.data.items():
        print("Objects for:", tableName)
        for obj in values:
            print("     ", obj)
elif action == "encrypt":

    print("Bin test (w/ encrypt)")

    db = Database()
    db.add_table(User)
    action = input("action (save/load): ")
    key = Fernet.generate_key()

    if action == "save":
        me = User(username = "encrypted_okzyrox", password = "hello")
        db.add_record("User", me)

        for i in range(0, 10):
            person = User(username = "e_testuser" + str(i), password = "test")
            db.add_record("User", person)

        db.save_to_file("testdata/encrypted_users.scdb", "bin", key)

    action = input("action (save/load): ")
    if action == "load":
        loaded_db = db.load_from_file("testdata/encrypted_users.scdb", key)

        for tableName, values in loaded_db.data.items():
            print("Objects for:", tableName)
            for obj in values:
                print("     ", obj)
    else:
        print("invalid action, cancelling")