# XML <-> yams equivalence
from cubicweb.xy import xy
xy.add_equivalence('Blog', 'sioc:Weblog')
xy.add_equivalence('BlogEntry', 'sioc:BlogPost')
xy.add_equivalence('BlogEntry title', 'dcterms:title')
xy.add_equivalence('BlogEntry content', 'sioc:content')
