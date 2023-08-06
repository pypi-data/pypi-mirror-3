# add group "owners" in transition "publish" of BlogEntry workflow permissions
rql('SET T require_group G WHERE G name "owners", T transition_of W, '
    'T name "publish", W workflow_of ET, ET name "BlogEntry"')
commit()
