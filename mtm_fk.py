from impl.scsl import Database, Table, StringField, IntegerField, RelationField, RelationType, ManyToManyField

db = Database()

class User(Table):
    id = IntegerField(primary_key=True)
    name = StringField()

class Tag(Table):
    id = IntegerField(primary_key=True)
    name = StringField()

class Post(Table):
    id = IntegerField(primary_key=True)
    title = StringField()
    content = StringField()
    creator = RelationField(to=User, relation_type=RelationType.ONE_TO_MANY, foreign_key="user_id")
    tags = ManyToManyField(to=Tag, relation_table_name="post_tags")

class PostTag(Table):
    post = RelationField(to=Post, relation_type=RelationType.ONE_TO_MANY)
    tag = RelationField(to=Tag, relation_type=RelationType.ONE_TO_MANY)

db.add_table(User)
db.add_table(Post)
db.add_table(Tag)
db.add_table(PostTag) 
# kinda creates duplicates in the schema files,  it makes things kinda clear but i should improve this when im less tired

user1 = User(id=1, name="okzyrox")
user2 = User(id=2, name="okzyrox2")

db.add_record("User", user1)
db.add_record("User", user2)

tag1 = Tag(id=1, name="Programming")
tag2 = Tag(id=2, name="Epic")
tag3 = Tag(id=3, name="SCSL")

db.add_record("Tag", tag1)
db.add_record("Tag", tag2)
db.add_record("Tag", tag3)

# Create posts
post1 = Post(
    id=1,
    title="My First Post",
    content="This is a post about programming",
    creator=user1,
    tags = [tag1, tag3]
)

post2 = Post(
    id=2,
    title="SCSL is Epic",
    content="I love using SCSL for database management",
    creator=user2,
    tags = [tag2, tag3]
)

db.add_record("Post", post1)
db.add_record("Post", post2)

# currently for testing, ideally is automatic
post_tag1 = PostTag(post=post1, tag=tag1)
post_tag2 = PostTag(post=post1, tag=tag3)
post_tag3 = PostTag(post=post2, tag=tag2)
post_tag4 = PostTag(post=post2, tag=tag3)

db.add_record("PostTag", post_tag1)
db.add_record("PostTag", post_tag2)
db.add_record("PostTag", post_tag3)
db.add_record("PostTag", post_tag4)

db.save_to_file("testdata/mtm_fk.scsl", "scsl")
db.save_to_file("testdata/mtm_fk.json", "json")
db.save_to_file("testdata/mtm_fk.scdb", "bin")

loaded_db = Database.load_from_file("testdata/mtm_fk.scdb")

print("Users:")
for user in loaded_db.all("User"):
    print(f"  {user}")

print("\nPosts:")
for post in loaded_db.all("Post"):
    print(f"  {post}")
    print(f"    Creator: {post.creator.name}")
    post_tags = loaded_db.get("PostTag", post=post)
    tags = [pt.tag.name for pt in post_tags]
    print(f"    Tags: {', '.join(tags)}")

print("\nTags:")
for tag in loaded_db.all("Tag"):
    print(f"  {tag}")