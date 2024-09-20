## TITLE: SCSL official implementation
## CC: okzyrox
## LICENSE: MIT


import json
import enum
import pickle
from typing import Any, Dict, List, Optional, Type, Union

class RelationType(enum.Enum):
    ONE_TO_ONE = "OneToOne"
    ONE_TO_MANY = "OneToMany"
    MANY_TO_MANY = "ManyToMany"

    def __str__(self):
        return self.value


class Field:
    def __init__(self, field_type: Type, **kwargs):
        self.field_type = field_type
        self.attributes = kwargs
        self.primary_key = kwargs.get('primary_key', False)
        self.null = kwargs.get('null', False)
        self.blank = kwargs.get('blank', False)
        self.default = kwargs.get('default', None)
        self.unique = kwargs.get('unique', False)

    def to_dict(self):
        return {
            "field_type": self.field_type.__name__,
            "attributes": self.attributes
        }

    def validate(self, value):
        if value is None and not self.null:
            raise ValueError(f"Field cannot be null")
        if value is not None and not isinstance(value, self.field_type):
            raise TypeError(f"Expected {self.field_type.__name__}, got {type(value).__name__}")
        return value

class StringField(Field):
    def __init__(self, max_length: int = 255, **kwargs):
        super().__init__(str, max_length=max_length, **kwargs)

class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__(int, **kwargs)
        self.min_value = kwargs.get('min_value', 0)
        self.max_value = kwargs.get('max_value', 2147483647)
    
    def validate(self, value):
        value = super().validate(value)
        if value is not None:
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"Value {value} is less than minimum {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"Value {value} is greater than maximum {self.max_value}")
        return value

class FloatField(Field):
    def __init__(self, **kwargs):
        super().__init__(float, **kwargs)
        self.min_value = kwargs.get('min_value', 0.0)
        self.max_value = kwargs.get('max_value', 2147483647.0)
    
    def validate(self, value):
        value = super().validate(value)
        if value is not None:
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"Value {value} is less than minimum {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"Value {value} is greater than maximum {self.max_value}")
        return value

class BooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__(bool, **kwargs)


class RelationField(Field):
    def __init__(self, to: Union[str, Type['Table']], relation_type: RelationType, **kwargs):
        super().__init__(to, relation_type=relation_type, **kwargs)
        self.to = to
        self.relation_type = relation_type

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["to"] = self.to if isinstance(self.to, str) else self.to.__name__
        base_dict["relation_type"] = str(self.relation_type)
        return base_dict

class TableMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
                attrs[key] = None
        attrs['_fields'] = fields
        return super().__new__(cls, name, bases, attrs)

class Table(metaclass=TableMeta):
    def __init__(self, **kwargs):
        for key, field in self._fields.items():
            value = kwargs.get(key, field.default)
            setattr(self, key, field.validate(value))

    def __setattr__(self, key, value):
        if key in self._fields:
            value = self._fields[key].validate(value)
        super().__setattr__(key, value)

    def to_dict(self) -> Dict[str, Any]:
        return {key: getattr(self, key) for key in self._fields}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=self._json_serializer)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Table':
        return cls.from_dict(json.loads(json_str))

    @staticmethod
    def _json_serializer(obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, bytes):
            return obj.hex()
        elif isinstance(obj, Table):
            return obj.to_dict()
        elif isinstance(obj, RelationType):
            return str(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    def __str__(self):
        # i only recently learnt of self.__class__.__name__
        # that wouldve saved sooo many headaches in previous projects if i knew
        return str(self.__class__.__name__) + ": " + ', '.join([f"{key} = {value}" for key, value in self.to_dict().items()])


    # might add a to_table_str function which prints it out prettily looking like a 
    # table with splitters and padding and organization
    # would be cool

class Database:
    def __init__(self):
        self.tables: Dict[str, Type[Table]] = {}
        self.data: Dict[str, List[Table]] = {}

    def add_table(self, table: Type[Table]):
        self.tables[table.__name__] = table
        self.data[table.__name__] = []

    def get_table(self, table_name: str) -> Optional[Type[Table]]:
        return self.tables.get(table_name)

    def add_record(self, table_name: str, record: Table):
        if table_name in self.data:
            self.data[table_name].append(record)
        else:
            raise ValueError(f"Table {table_name} does not exist in the database")

    def to_json(self) -> str:
        schema = {}
        for name, table in self.tables.items():
            schema[name] = {}
            for field_name, field in table._fields.items():
                field_dict = field.to_dict()
                if isinstance(field, RelationField):
                    field_dict["relation_type"] = str(field.relation_type)
                schema[name][field_name] = field_dict
        return json.dumps(schema, indent=4, default=Table._json_serializer)

    def save_to_file(self, filename: str):
        with open(filename, 'wb') as f:
            # todo:
                # standard encoding style (no pickle?)
                # encryption with key + randomization/salt?
            pickle.dump((self.tables, self.data), f)

    @classmethod
    def load_from_file(cls, filename: str) -> 'Database':
        with open(filename, 'rb') as f:
            tables, data = pickle.load(f)
        db = cls()
        db.tables = tables
        db.data = data
        return db

# Test stuff
if __name__ == "__main__":
    class Person(Table):
        name = StringField(max_length=100)
        age = IntegerField(min_value=0, max_value=120)
        is_active = BooleanField(default=True)

    class Job(Table):
        title = StringField(max_length=100)
        salary = FloatField(min_value=0)
        person = RelationField(to=Person, relation_type=RelationType.ONE_TO_ONE, null=True)

    db = Database()
    db.add_table(Person)
    db.add_table(Job)

    person = Person(name="Alice", age=30)
    db.add_record("Person", person)

    job = Job(title="Software Developer", salary=75000.0, person=person)
    db.add_record("Job", job)

    for tableName, values in db.data.items():
        print("Objects for:", tableName)
        for obj in values:
            print("     ", obj)

    
    print("Changing")
    # Validation failures cause exception, so youd want to design around try:, except: blocks otherwise your database system might crash :)
    job.salary = 55000.0
    person.name = "James"
    person.age = 24

    try:
        person.age = 121
    except Exception as e: # Fails as its above the maximum
        print(e)
    
    newJob = Job(title = "Database Engineer", salary=1.0)
    job.person = None 
    # The tables are linked to the database tables, so you dont have to worry about mismatches and outdated version of tables
    newJob.person = person
    db.add_record("Job", newJob)
    print("Saving")
    db.save_to_file("people.db")
    print("Reloading")
    loaded_db = Database.load_from_file("people.db")

    with open("schema.json", 'w') as schemaFile:
        schemaFile.write(loaded_db.to_json())
        # Currently it is designed to only write the schema to a json file
        # whether i call this a security feature or lacking of features i dont know..
    for tableName, values in loaded_db.data.items():
        print("Objects for:", tableName)
        for obj in values:
            print("     ", obj)