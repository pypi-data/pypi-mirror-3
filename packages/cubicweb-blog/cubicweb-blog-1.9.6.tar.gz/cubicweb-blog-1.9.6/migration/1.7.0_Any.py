add_relation_definition('BlogEntry',  'in_state', 'State')
add_relation_definition('TrInfo',  'wf_info_for', 'BlogEntry')
add_relation_definition('BlogEntry',  'custom_workflow', 'Workflow')


# add BlogEntry workflow
if confirm('add blog entry workflow'):
    bwf = add_workflow(_('default BlogEntry workflow'), 'BlogEntry')

    draft = bwf.add_state(_('draft'), initial=True)
    published = bwf.add_state(_('published'))

    publish = bwf.add_transition(_('publish'), draft, published,
                                 ('managers',))
    commit()

# set state to published for already existing blog entries
blogentries = rql('Any B WHERE B is BlogEntry')

for eid, in blogentries:
    session.unsafe_execute('SET B in_state S WHERE S name "published", '
                           'S state_of WF, WF name "default BlogEntry workflow", '
                           'B eid %(b)s',
                           {'b': eid}, 'b')

commit()
