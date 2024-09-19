# "Super Cool database stuff"

## But why?

Personally,  I hate the SQL syntax and it's pretty widespread without having any major competitors or other options (that I know of) that provide a more programmatic syntax with more types.
### File types:
- `scql` - Super cool query language (used for queries and accessing)
- `scsl` - Super cool structure language (used to make databases)
- `scdb` - Super cool data-base (the database)
## Theoretical Benefits

- Support for Schema functions, allowing utility tasks to be written in the Schema code to run across the database (such as testing, adding or removing tables/rows/entries, checking for invalid entries)
- Encryptable with a Private Key, and is only decrypted for accessing clients, the file itself is never decrypted to keep it secure
- More types / Advanced Types
### Standard Table Types:
- `Char`
- `String`
	- `String {size: Integer}` Default max size is `1024`.
- `Bool`
- `Integer` (`Integer8, Integer16, Integer32, Integer64, Integer128`) Can be shorthanded as `Int8, Int16, Int32, Int64, Int128` or `i8, i16, i32, i64, i128`
- `Float` (`Float8, Float16, Float32, Float64, Float128`) Can be shortened as `f8, f16, f32, f64, f128`
- `Date` - Represents a date with `day`, `month` and `year` as `DD-MM-YYYY` in converted form.
- `Time` - Represents a time with `hour`, `minute`, and `seconds` as `HH:MM:SS`
- `DateTime` - Represents a combination of both `Date` and `Time`.
- `Json` (also includes `{maxDepth: Integer}`, to indicate how far down a json sequence is allowed to go for storage concerns)
- `Binary`
	- `Binary {size: Integer}`
	- `Binary<BinaryType>` - Includes: `Tiny (255 bytes)`, `Medium (65,535 bytes or 65KB)`, `Big (16,777,215 bytes or 16MB)`,  `Mega (536,870,912 bytes or 512MB)`
- `Array`
     - `Array<Type/Table>`. Allows for specific arrays of types
     - `Array {min: Integer, max:Integer}`. Indicates minimum and maximum values for object creation/updating 
     - Blank Arrays allow any type, and have a maximum of 255 items.
- `Enum`
     - Enums can be defined within the database Table, and are assigned a unique value towards the specified name. The name acts as a primary key.
     - Example:
- `Relation`
	- `Relation<RelationType>`. Defines the relation type. Of: `OneToOne`, `OneToMany` and `ManyToMany`

Additionally:
- `null`, only used for blank spaces, such as those without default values


Simple example:

```ruby
# simple.scsl

Table Person:
	String firstName
	String lastName
	Int age {min: 0, max: 100}
```

Enum example:
```ruby
# enums.scsl

Enum Job:
    Accountant as 1
    Teacher as 2
    Ceo as 3
Enum Title:
    Mr as "Mr." 
    Mrs as "Mrs."
    Dr as "Dr."

Table Person:
    String name
    Enum.Job job
    Enum.Title title

```

Relations can also be created as such:
```ruby
# jobs.scsl
Table Job:
	Int64 id {primaryKey, upSequence, start: 0}

	String jobName {null: False}

Table User:
	Int64 id {primaryKey, upSequence, start: 0}

	String firstName {null: False}

RelationTable UserJobs:
	Relation<OneToOne, User> userAcc
	Relation<OneToMany, Job> userJob {uses: id} # Can also specify the primaryKey field manually, but it will automatically use either the first or only primaryKey field.
```

Attributes are added alongside field definitions to define their special properties, the following are the list of attributes.
- `primaryKey` - Only allowed 1-2 times per table, not all fields can be primaryKeys
- `upSequence` + `downSequence` - Used for `Int` and also requires `start` and `primaryKey`. Indicates the direction that new primary key ids should be created in. Default increment is 1.
- `autoIncrement: <Bool>` - Defines if new entities auto increment for an integer primaryKey
- `change: <Int>` Cannot be negative, indicates the increment / decrement.
- `start: <Int>` - Used in tandem with the previous one to indicate the starting value for the first entity in the Table
- `default: <String|Int|Float|Bool|Table|Json|Enum>` - Used to indicate the default value for the specific field on a table, can be of any type except array. Arrays are automatically empty on new entities.
- `null: <Bool>` - Indicates whether the field can be null or not. Default is `False`
- `blank: <Bool>` - Indicates whether the field can be blank or not, meaning it is never assigned a value. Cannot be used alongside `null:`. Default is `False`
- `uses: FieldName` - Indicates a specific field to use for a primaryKey, fails if the field does not exist or is not a primaryKey. Default uses the first or only primaryKey field in the table.
- `maxJsonDepth: <Integer>` - Indicates the maximum amount of chains, or nested json statements that a json field can have. The default max depth is `64`

## Accessing the table

Tables inside a database can be access through utility commands, rather than creating statements of code which can be generally unsafe or difficult to program which makes them unsafe.

```ruby
# getTables.scql

get * from User where: { 
	# '*' refers to all fields
	firstName == "John"
} as: {
	order: Descending,
	orderBy: User.id
}
# Returns all the users from the User table, where the firstName is John. It is returned in Descenging order, ordered by the Id of the user.

```

`scdb exec getTables.scql >> out.txt`
```python
# out.txt
<User>[id: 6, firstName: "John", lastName: "Steve"]
<User>[id: 5, firstName: "John", lastName: "Roberts"]
<User>[id: 2, firstName: "John", lastName: "Davids"]
<User>[id: 1, firstName: "John", lastName: "Test"]
```

```ruby
# getSpecific

get: {
	firstName,
	lastName
} from User # can be chained with more

# Only returns the a list of firstNames and lastNames for the Users gotten. Also works for Json.
```

```ruby
# updateTables

update User with: {
	firstName = "John"
}
# Changes every uses firstName in the user table with "John"
```

```ruby
# updateTablesSpecific

update User where: {
	firstName == "John"
} with: {
	firstName = "Alex"
} 
# Updates all users named John from the User table, changing their firstName from John to Alex.
```

```ruby
# removeTables

remove User where: {
	firstName == "James"
}
# Removes all users from the User table where their name is James 
```

```ruby
# createNewEntity

create User with: {
	firstName = "Steve",
	lastName = "Minecraft",
	age = 34
}
# Inserts into the table with the specified fields. Any non null or non blank field that arent provided will cause it to error out.
# If they have
```

Other modifiers are added by doing `but: {}`
Modifier list:
- `limit = <Int>` - Limits the responses and indexes entities

All table queries are checked for errors, problems, inefficient statements and unsafe executions before running. In addition you can pass variables via the command. In addition, Table queries can be tested using:
`scdc test getTables.scql >> debug.txt`
`test` includes extra debug information into the output file.

```ruby
# getTablesByName.scql

get * from User where: {
	firstName == &("cmdFirstName")
} as: {
	order: Descending,
	orderBy: User.id
}
# Returns all the users from the User table, where the firstName is passed by the cmd line. It is returned in Descenging order, ordered by the Id of the user.
```

`scdb exec getTablesByName.scql -a:cmdFirstName="John" >> out.txt`

Additional commands are prefixed by `-a:<cmd>=` and then a valid type. Such as: `String`, `Int`, `Float`, `Bool` as `True` or `False`, `Date` as `"DD-MM-YYYY"`, `Time` as `"HH:MM:SS"`, `DateTime` as `"DD-MM-YYYY|HH:MM:SS"`, `Enum` as `Enum.<field>`

Plus, you can add `-o:json` to get a `json` representation of the data changed (only works for `get`)

`scdb exec getTables.scql -o:json >> out.json

```json
{
	"User": [
		{
			"id": 6, "firstName": "John", "lastName": "Steve"
		},
		{
			"id": 5, "firstName": "John", "lastName": "Roberts"
		},
		{
			"id": 2, "firstName": "John", "lastName": "Davids"
		},
		{
			"id": 1, "firstName": "John", "lastName": "Test"
		}
	]
}
```
Note:
- Enums in `json` are represented by their `as` field. So using:
```ruby

Enum JobType:
	Programmer as 1
	Teacher as 2
	President as 3
```

Would result in the `Programmer` `enum` being written as `1` in the `json`.