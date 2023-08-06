# postcreate script. You could setup a workflow here for example

# BlogEntry workflow
bwf = add_workflow(_('default BlogEntry workflow'), 'BlogEntry')

draft = bwf.add_state(_('draft'), initial=True)
published = bwf.add_state(_('published'))

publish = bwf.add_transition(_('publish'), draft, published,
                             ('managers', 'owners'))

