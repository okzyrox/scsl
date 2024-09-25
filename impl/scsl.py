## TITLE: SCSL official implementation
## CC: okzyrox
## LICENSE: MIT


import os
import json
import enum
from cryptography.fernet import Fernet
from typing import Any, Dict, List, Optional, Type, Union
from datetime import date, time, datetime

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

class ArrayField(Field):
    def __init__(self, item_type: Type, max_length: int = None, **kwargs):
        super().__init__(list, **kwargs)
        self.item_type = item_type
        self.max_length = max_length
    
    def to_dict(self):
        return {
            "field_type": "list",
            "attributes": {
                "array_type": self.item_type.__name__,
                "max_length": self.max_length
            }
        }

    def validate(self, value):
        value = super().validate(value)
        if value is not None:
            if self.max_length is not None and len(value) > self.max_length:
                raise ValueError(f"Array length {len(value)} is too high. ({len(value)} / {self.max_length}")
            for item in value:
                if not isinstance(item, self.item_type):
                    raise TypeError(f"Expected {self.item_type.__name__}, got {type(item).__name__}")
        return value

class DateField(Field):
    def __init__(self, **kwargs):
        super().__init__(date, **kwargs)

    def validate(self, value):
        value = super().validate(value)
        if value is not None and not isinstance(value, date):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Invalid date format: {value}")
        return value

class TimeField(Field):
    def __init__(self, **kwargs):
        super().__init__(time, **kwargs)

    def validate(self, value):
        value = super().validate(value)
        if value is not None and not isinstance(value, time):
            try:
                return time.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Invalid time format: {value}")
        return value

class DateTimeField(Field):
    def __init__(self, **kwargs):
        super().__init__(datetime, **kwargs)

    def validate(self, value):
        value = super().validate(value)
        if value is not None and not isinstance(value, datetime):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {value}")
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
        elif isinstance(obj, (date, time, datetime)):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [Table._json_serializer(item) for item in obj]
        raise TypeError(f"Type {type(obj)} not serializable")

    def __str__(self):
        # i only recently learnt of self.__class__.__name__
        # that wouldve saved sooo many headaches in previous projects if i knew
        return str(self.__class__.__name__) + "(" + ', '.join([f"{key} = {value}" for key, value in self.to_dict().items()]) + ")"

    def __repr__(self):
        return str(self)


    # might add a to_table_str function which prints it out prettily looking like a 
    # table with splitters and padding and organization
    # would be cool

def python_type_to_scsl(python_type: str) -> str:
        match python_type:
            case "str": return "String"
            case "int": return "Integer"
            case "bool": return "Bool"
            case "float": return "Float"
            case "date": return "Date"
            case "time": return "Time"
            case "datetime": return "DateTime"
            case "list": return "Array"
            case _: return python_type  ## for models so they are supported
    
def python_str_to_type(python_str: str):
    match python_str:
        case "str": return str
        case "int": return int
        case "bool": return bool
        case _: return None

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
    
    def serialize_to_binary(self):
        import struct

        def encode_string(s):
            encoded = s.encode('utf-8')
            return struct.pack('!I', len(encoded)) + encoded

        def encode_value(value):
            if isinstance(value, str):
                return b'\x01' + encode_string(value)
            elif isinstance(value, int):
                return b'\x02' + struct.pack('!q', value)
            elif isinstance(value, float):
                return b'\x03' + struct.pack('!d', value)
            elif isinstance(value, bool):
                return b'\x04' + struct.pack('!?', value)
            elif value is None:
                return b'\x05'
            elif isinstance(value, Table):
                return b'\x06' + encode_string(value.__class__.__name__) + struct.pack('!q', id(value))
            elif isinstance(value, date):
                if isinstance(value, datetime):
                    return b'\x09' + struct.pack('!IIIIII', value.year, value.month, value.day, value.hour, value.minute, value.second)
                else:
                    return b'\x07' + struct.pack('!III', value.year, value.month, value.day)
            elif isinstance(value, time):
                return b'\x08' + struct.pack('!III', value.hour, value.minute, value.second)
            elif isinstance(value, list):
                encoded_list = b'\x0A' + struct.pack('!I', len(value))
                for item in value:
                    encoded_list += encode_value(item)
                return encoded_list
            else:
                raise ValueError(f"Unsupported type: {type(value)}")

        binary_data = b''

        # da tables (this took me too long to figure out)
        binary_data += struct.pack('!I', len(self.tables))
        for table_name, table_class in self.tables.items():
            binary_data += encode_string(table_name)
            binary_data += struct.pack('!I', len(table_class._fields))
            for field_name, field in table_class._fields.items():
                binary_data += encode_string(field_name)
                binary_data += encode_string(field.__class__.__name__)
                if isinstance(field, RelationField):
                    binary_data += encode_string(field.to if isinstance(field.to, str) else field.to.__name__)
                    binary_data += encode_string(str(field.relation_type))
                elif isinstance(field, ArrayField):
                    binary_data += encode_string(field.item_type.__name__)
                    binary_data += struct.pack('!I', field.max_length if field.max_length is not None else 0)

        # cba to write a json converter for all the types
        # because that sucks
        binary_data += struct.pack('!I', len(self.data))
        for table_name, records in self.data.items():
            binary_data += encode_string(table_name)
            binary_data += struct.pack('!I', len(records))
            for record in records:
                binary_data += struct.pack('!I', len(record._fields))
                for field_name, field in record._fields.items():
                    binary_data += encode_string(field_name)
                    value = getattr(record, field_name)
                    binary_data += encode_value(value)

        return binary_data

    def get(self, table_name, **kwargs) -> List[Table] | Table | None:
        table = self.get_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist in the database")
        records = [record for record in self.data[table_name] if all(getattr(record, field_name) == value for field_name, value in kwargs.items())]
        if len(records) == 1:
            return records[0]
        elif len(records) == 0:
            return None
        return records
    
    def all(self, table_name) -> List[Table]:
        table = self.get_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist in the database")
        return self.data[table_name]

    @classmethod
    def deserialize_from_binary(cls, binary_data):
        ## after reading the documentation far too many times
        ## i still dont know what its doing entirely
        ## but hey we got binary encoding for data
        import struct

        def decode_string():
            nonlocal index
            length = struct.unpack('!I', binary_data[index:index+4])[0]
            index += 4
            string = binary_data[index:index+length].decode('utf-8')
            index += length
            return string

        def decode_value():
            nonlocal index
            value_type = binary_data[index]
            index += 1
            if value_type == 0x01:
                return decode_string()
            elif value_type == 0x02:
                value = struct.unpack('!q', binary_data[index:index+8])[0]
                index += 8
                return value
            elif value_type == 0x03:
                value = struct.unpack('!d', binary_data[index:index+8])[0]
                index += 8
                return value
            elif value_type == 0x04:
                value = struct.unpack('!?', binary_data[index:index+1])[0]
                index += 1
                return value
            elif value_type == 0x05:
                return None
            elif value_type == 0x06:
                table_name = decode_string()
                obj_id = struct.unpack('!q', binary_data[index:index+8])[0]
                index += 8
                return (table_name, obj_id)
            elif value_type == 0x07:
                year, month, day = struct.unpack('!III', binary_data[index:index+12])
                index += 12
                return date(year, month, day)
            elif value_type == 0x08:
                hour, minute, second = struct.unpack('!III', binary_data[index:index+12])
                index += 12
                return time(hour, minute, second)
            elif value_type == 0x09:
                year, month, day, hour, minute, second = struct.unpack('!IIIIII', binary_data[index:index+24])
                index += 24
                return datetime(year, month, day, hour, minute, second)
            elif value_type == 0x0A:
                array_length = struct.unpack('!I', binary_data[index:index+4])[0]
                index += 4
                return [decode_value() for _ in range(array_length)]
            else:
                raise ValueError(f"Unsupported value type: {value_type}")

        index = 0
        db = cls()

        # tables
        num_tables = struct.unpack('!I', binary_data[index:index+4])[0]
        index += 4
        for _ in range(num_tables):
            table_name = decode_string()
            num_fields = struct.unpack('!I', binary_data[index:index+4])[0]
            index += 4
            fields = {}
            for _ in range(num_fields):
                field_name = decode_string()
                field_type = decode_string()
                if field_type == 'RelationField':
                    to = decode_string()
                    relation_type = RelationType(decode_string())
                    fields[field_name] = RelationField(to=to, relation_type=relation_type)
                elif field_type == 'ArrayField':
                    item_type_name = decode_string()
                    item_type = getattr(__builtins__, item_type_name, None)
                    if item_type is None:
                        item_type = python_str_to_type(item_type_name)
                    if item_type is None:
                        raise ValueError(f"Unknown type: {item_type_name}")
                    max_length = struct.unpack('!I', binary_data[index:index+4])[0]
                    index += 4
                    fields[field_name] = ArrayField(item_type, max_length if max_length > 0 else None)
                else:
                    field_class = globals()[field_type]
                    fields[field_name] = field_class()
            table_class = type(table_name, (Table,), fields)
            db.add_table(table_class)

        # data
        num_data_tables = struct.unpack('!I', binary_data[index:index+4])[0]
        index += 4
        for _ in range(num_data_tables):
            table_name = decode_string()
            num_records = struct.unpack('!I', binary_data[index:index+4])[0]
            index += 4
            for _ in range(num_records):
                num_fields = struct.unpack('!I', binary_data[index:index+4])[0]
                index += 4
                record_data = {}
                for _ in range(num_fields):
                    field_name = decode_string()
                    value = decode_value()
                    field = db.tables[table_name]._fields[field_name]
                    if isinstance(field, DateTimeField) and isinstance(value, date):
                        # TODO: fix time
                        value = datetime.combine(value, time())
                    record_data[field_name] = value
                record = db.tables[table_name](**record_data)
                db.add_record(table_name, record)

        return db

    def to_scsl(self) -> str:
        schema = []
        for table_name, table in self.tables.items():
            schema.append(f"Table {table_name}:")
            for field_name, field in table._fields.items():
                field_def = f"    {python_type_to_scsl(field.field_type.__name__)}"
                if isinstance(field, ArrayField):
                    field_def += f"<{python_type_to_scsl(field.item_type.__name__)}>"
                field_def += f" {field_name}"
                attributes = []
                if field.primary_key:
                    attributes.append("primaryKey")
                if field.null:
                    attributes.append("null: True")
                if field.unique:
                    attributes.append("unique")
                if field.default is not None:
                    attributes.append(f"default: {repr(field.default)}")
                if isinstance(field, StringField):
                    attributes.append(f"size: {field.attributes.get('max_length', 255)}")
                if isinstance(field, (IntegerField, FloatField)):
                    if field.min_value is not None:
                        attributes.append(f"min: {field.min_value}")
                    if field.max_value is not None:
                        attributes.append(f"max: {field.max_value}")
                if isinstance(field, ArrayField):
                    if field.max_length is not None:
                        attributes.append(f"max_length: {field.max_length}")
                # wack ngl, might remove it but i gotta say it looks way cleaner than the original in the write up file

                # Torn between "Relation:ONE_TO_ONE" or "Relation<ONE_TO_ONE>"
                # using the latter right now because it makes the attribute clearer to see
                if isinstance(field, RelationField):
                    #to_table = field.to if isinstance(field.to, str) else field.to.__name__
                    attributes.append(f"Relation<{field.relation_type}>")
                
                if attributes:
                    field_def += " {" + ", ".join(attributes) + "}"
                schema.append(field_def)
            schema.append("") # padding between tables
        return "\n".join(schema)

    def save_to_file(self, filename: str, format: str, encryption_key = None):
        ## Formats:
        ## 'json', 'scsl', 'binary/bin/scdb'

        ## 'json' returns a jsonization of the schema made to make the database
        ## 'scsl' does the same but for the scsl format (still WIP)
        ## 'bin/binary/scdb' is where the actual objects and data in the db are stored.
        ## might split the schema part from the data part later idk


        if format == "binary" or format == "bin" or format == "scdb":
            binary_data = self.serialize_to_binary()
            if encryption_key:
                f = Fernet(encryption_key)
                encrypted_data = f.encrypt(binary_data)
                with open(filename, 'wb') as file:
                    file.write(encrypted_data)
            else:
                with open(filename, 'wb') as file:
                    file.write(binary_data)
        elif format == 'json':
            with open(filename, 'w') as f:
                json.dump(json.loads(self.to_json()), f, indent=4)
        elif format == 'scsl':
            with open(filename, 'w') as f:
                f.write(self.to_scsl())
        else:
            raise ValueError(f"Unsupported format: {format}")

    @classmethod
    def load_from_file(cls, filename: str, encryption_key = None) -> 'Database':
        name, ext = os.path.splitext(filename)
        if ext == ".bin" or ext == ".scdb":
            with open(filename, 'rb') as f:
                data = f.read()
            if encryption_key:
                f = Fernet(encryption_key)
                decrypted_data = f.decrypt(data)
            else:
                decrypted_data = data
            return cls.deserialize_from_binary(decrypted_data)
        else:
            raise ValueError(f"Invalid Database format to load from: {ext}")