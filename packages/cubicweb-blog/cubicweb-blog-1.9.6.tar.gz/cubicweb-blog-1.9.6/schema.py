from yams.buildobjs import EntityType, String, RichString, SubjectRelation, RelationDefinition
from cubicweb.schema import WorkflowableEntityType, ERQLExpression

class Blog(EntityType):
    title = String(maxsize=50, required=True)
    description = RichString()
    rss_url = String(maxsize=128, description=_('blog\'s rss url (useful for when using external site such as feedburner)'))

class BlogEntry(WorkflowableEntityType):
    __permissions__ = {
        'read': ('managers', 'users', ERQLExpression('X in_state S, S name "published"'),),
        'add': ('managers', 'users'),
        'update': ('managers', 'owners'),
        'delete': ('managers', 'owners')
        }
    title = String(required=True, fulltextindexed=True, maxsize=256)
    content = RichString(required=True, fulltextindexed=True)
    entry_of = SubjectRelation('Blog')
    same_as = SubjectRelation('ExternalUri')

class MicroBlog(EntityType):
    title = String(maxsize=50, required=True)
    description = RichString()

class MicroBlogEntry(EntityType):
    __permissions__ = {
        'read': ('managers', 'users'),
        'add': ('managers', 'users'),
        'update': ('managers', 'owners'),
        'delete': ('managers', 'owners')
        }
    content = RichString(required=True, fulltextindexed=True)
    entry_of = SubjectRelation('MicroBlog')
    same_as = SubjectRelation('ExternalUri')

class UserAccount(EntityType):
    name = String(required=True) # see foaf:accountName

class has_creator(RelationDefinition):
    subject = ('BlogEntry', 'MicroBlogEntry')
    object = 'UserAccount'

class has_avatar(RelationDefinition):
    subject = 'UserAccount'
    object = 'ExternalUri'

