__import__('pkg_resources').declare_namespace(__name__)

# pickler tools export
from sphinx.webtools.pickler_tools import update_docs, reformat_content_links,\
                                    PicklerContentManager, get_genentries,\
                                    get_modentries

# search tools export
from sphinx.webtools.search_tools import highlight, search
