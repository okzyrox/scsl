### scsl python TODO LIST:
- [x] saving to json (schema)
- [x] saving to scsl (schema)
- [x] saving to an encoded db file
- [x] loading from an encoded db file
- [ ] Tables:
    - [x] Creation
    - [x] Modification
    - [ ] querying
    - [ ] safe deletion (no remnants, checks for relations, etc)
- [ ] type support:
    - [x] Char
    - [x] String
    - [x] Integer
    - [x] Float
    - [ ] Date
    - [ ] Time
    - [ ] DateTime
    - [ ] Array
    - [ ] Binary:
        - [ ] Sizeable Binary
        - [ ] Small
        - [ ] Medium
        - [ ] Big
        - [ ] Mega
    - [ ] Json
    - [ ] Table Enums
    - [x] Relations:
        - [x] OneToOne
        - [ ] OneToMany
        - [ ] ManyToMany
    
`note: attribute support is only finished if it has proper implementaiton and validation`
- [ ] Attribute support:
    - [ ] primary key
        - [ ] pk uses specific:
    - [x] min value + max value
    - [x] default
    - [x] null
    - [ ] blank
    - [ ] jsonMaxDepth
    - [ ] unique
        - [ ] start
        - [ ] change
        - [ ] sequence direction (also needs support for overflow, underflow, etc)

    - [ ] attribute pairs validation (suchas: `default` cant be used with `null=false`)