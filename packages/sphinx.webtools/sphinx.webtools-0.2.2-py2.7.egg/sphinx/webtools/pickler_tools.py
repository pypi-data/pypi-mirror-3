# python import
import os
import shutil
import sys
from cPickle import Unpickler

# pkg_resources import
from pkg_resources import resource_filename

# sphinx import
from sphinx.application import Sphinx

# genshi import for xml reformat
from genshi import XML
from genshi.filters.transform import Transformer

def update_docs(source_dir, doc_dir):
    """Build the Sphinx documentation from the source_dir to the doc_dir. The
    doc_dir is previously remove. We use the *web* builder by default to obtain
    the pickle files in the doc_dir.

    @param source_dir: Sphinx source folder of the project
    @type source_dir: str

    @param doc_dir: Plugin Sphinx web folder for output
    @type doc_dir: str
    """
    # check the source dir
    try:
        if not os.path.exists(source_dir):
            msg = '<div><b>Source directory not found:</b>'
            msg += ' %s</div>' % source_dir
            return XML(msg)
    except Exception, e:
        msg = '<div><b>Source dir error:</b> %s</div>' % e
        return XML(msg)

    # create the doc dir if needed
    try:
        # remove old docs
        if os.path.exists(doc_dir):
            shutil.rmtree(doc_dir)

        # re-create the dest dir
        os.mkdir(doc_dir)

    except Exception, e:
        msg = '<div><b>Doc dir error:</b> %s</div>' % e
        return XML(msg)

    # output .doctrees path
    doctree_dir = os.path.join(doc_dir, '.doctrees')

    # set the web builder name
    builder_name = 'web'

    # sphinx settings
    conf_overrides = {}
    fresh_env = False

    ## create sphinx application
    try:
        app = Sphinx(source_dir, source_dir, doc_dir, doctree_dir,
                    builder_name, conf_overrides, sys.stdout, sys.stderr,
                    fresh_env)

    except Exception, e:
        msg = '<div><b>Sphinx error:</b> %s</div>' % e
        return XML(msg)

    ## build the documentation
    try:
        app.builder.build_all()
    except Exception, e:
        # can't manage the following error
        # No such file or directory: '.../sphinx/web/webconf.py'
        msg = '<div><b>Build error:</b> %s</div>' % e
        return XML(msg)

    return None

def get_pickler(doc_dir, filename):
    """Returns the pickler object corresponding to a file from the the
    documentation source directory. Return None in case of error.

    @param doc_dir: web documention directory
    @type doc_dir: str

    @param filename: filename of the pickle file to load
    @type filename: str
    """
    try:
        # load index pickle
        pickler_path = os.path.join(doc_dir, filename)
        # open index pickler file
        pickler_file = open(pickler_path, 'rb')
        # load pickler object
        pickler_obj = Unpickler(pickler_file).load()
        # close file
        pickler_file.close()
        # return the founded object
        return pickler_obj

    except:
        return None

def reformat_xml_content(text, id_):
    """Returns text as valid XML and removes junk characters.
    """
    text = '<div class="%s">%s</div>' % (id_, text)
    text = text.replace('&#8217;', '\'')
    return text

class PicklerContentManager(object):
    """Manage contents (relative links, table of content, body) from a pickler
    source. Returns content as str or XML for web integration.
    """

    def __init__(self, base_url, doc_dir, pickler_url):
        """Init the manager with given variables about documentation source and
        web base url.

        @param base_url: project base url
        @type base_url: str

        @param doc_dir: web documention directory
        @type doc_dir: str

        @param pickler_url: path to the current page pickler source
        @type pickler_url: str
        """
        # set the base url
        self.__base_url = base_url

        # build filename
        pickler_filename = '%s.fpickle' % pickler_url

        # get pickler object
        self.__content_pickler = get_pickler(doc_dir, pickler_filename)

    def get_rellinks(self):
        """Returns list of relative links in the current page as XML Stream.
        """
        # little check
        if not self.__content_pickler:
            return

        # rellinks to parse
        rellinks = self.__content_pickler['rellinks']

        # result links init
        result = list()

        # update result with reformatted links
        for link in rellinks:
            try:
                link = map(str, link)
            except Exception:
                link = map(lambda v: getattr(v, '_args', (v,))[0], link)
                
            title = link[1].replace('&#8217;', '\'')

            url = '%s?action=%s&item=%s' % (self.__base_url, link[-1], link[0])
            result.append(
                {
                    'category': link[-1],
                    'title':title,
                    'url':url,
                    }
                )

        # return result links
        return result

    def get_toc(self):
        """Returns the table of content part of a pickler file as XML Stream.
        """
        # little check
        if not self.__content_pickler:
            return

        # return formatted toc
        toc = self.__content_pickler['toc']
        result = reformat_xml_content(toc, 'toc')
        return result

    def get_body(self):
        """Returns the body part of a pickler file as str.
        """
        # little check
        if not self.__content_pickler:
            return

        # return formatted toc
        body = self.__content_pickler['body']
        result = reformat_xml_content(body, 'body')
        return result

class ContentLinkReformatter(object):
    """XML reformatter for content sphhinx link reformatting. Transforms
    relative sphinx generated links into valid sphinx plugin url with params.
    """

    def __init__(self, base_url, doc_dir):
        """Reformatter init, set a list of the current valid documentation
        project url.

        @param base_url: project base url
        @type base_url: str

        @param doc_dir: web documention directory
        @type doc_dir: str
        """
        # set the base url
        self.__base_url = base_url

        # links dict for url reformatting
        self.__links = None

        # get the index pickler object
        links_pickler = get_pickler(doc_dir, 'searchindex.pickle')

        # little check
        if links_pickler:
            # set page links variable
            self.__links = links_pickler['filenames']

    def __get_absolute_link(self, relative_url):
        """Build an absolute path form a relative link, ex.: '../test' ->
        'content/test' if 'content/test' exists in the previously __links list.

        @param relative_url: relative url to enhance
        @type relative_url: str
        """
        # get key for exploration
        result_key = relative_url.split('../')[-1]

        # init page in index variable
        page_in_index = None

        # get absolute url
        if not result_key.find('/#') == -1:
            # get key for exploration
            key_parts = result_key.split('/#')
            result_key = key_parts[0]
            page_in_index = '#%s' % key_parts[1]

        # build absolute url using docs links
        for project_link in self.__links:
            # get the sphink link on already formatted url
            #project_link = project_link.replace('sphinx?action=view&item=', '')
            if not project_link.find(result_key) == -1:
                if page_in_index:
                    return '%s%s' % (project_link, page_in_index)
                else:
                    return project_link

        return ''

    def __reformat_sphinx_links(self, link):
        """Builds a valid plugin link from a sphinx link, ex.: '../test/#1' ->
        'sphinx?action=view&item=content/test#1'

        @param link: relative url to reformat
        @type link: str
        """
        # non relative url
        if link.find('http://') == 0:
            return link

        # link within the page
        if link.startswith("#"):
            return link

        # parse sphinx url
        split_content = link.split('/')

        # remove junk value
        while '' in split_content:
            split_content.remove('')

        # rebuild link for trac
        result = '/'.join(split_content)

        # get absolute url
        if not result.find('../') == -1:
            result = self.__get_absolute_link(result)

        # final building
        result = '%s?action=view&item=%s' % (self.__base_url, result)

        # return result with valid link
        return result.replace('/#', '#')

    def replace_sphinx_links(self, name, event):
        """Finds and replaces links in a matched tag.
        """
        # attributes parsing
        attrs = event[1][1]

        # check for replace
        if attrs.get('class') == 'reference external':
            link = attrs.get('href')
            return self.__reformat_sphinx_links(link)

        # check for replace
        if attrs.get('class') in ('reference', 'reference internal'):
            link = attrs.get('href')
            return self.__reformat_sphinx_links(link)

        # nothing to do
        else:
            return attrs.get(name)

def reformat_content_links(base_url, doc_dir, content_xml):
    """Use genshi Transformer function to replace sphinx links in valid plugin
    links.

    @param base_url: project base url
    @type base_url: str

    @param doc_dir: web documention directory
    @type doc_dir: str

    @param content_xml: XML content to parse, using genshi Transformer function
    @type content_xml: genshi.XML
    """
    # init reformatter object
    reformatter = ContentLinkReformatter(base_url, doc_dir)

    # trigger the parsong for links updates
    return content_xml | Transformer('.//a').attr(
                                     'href', reformatter.replace_sphinx_links)

def format_entry_url(base_url, url_src):
    """Simple url reformat for plugin compliance.

    @param base_url: project base url
    @type base_url: str

    @param url_src: url to enhance
    @type url_src: str
    """
    if not len(url_src):
        return None

    # set the final base url
    base_url = '%s?action=view&item=' % base_url

    # simple reformat
    url = url_src.replace('../', base_url)
    url = url.replace('/#', '#')
    return url

def get_genentries(base_url, doc_dir):
    """Returns a list of the sphinx index entries of the project documentation.

    @param base_url: project base url
    @type base_url: str

    @param doc_dir: web documention directory
    @type doc_dir: str
    """
    # get the index pickler object
    content_pickler = get_pickler(doc_dir, 'genindex.fpickle')

    # little check
    if not content_pickler:
        return

    # read pickler
    entries = content_pickler['genindexentries']

    # result list
    result = list()

    for entry in entries:
        # list of links for the current letter
        links = list()
        # parse links
        for item in entry[1]:
            # link dict
            link = {
                'title': item[0],
                'url': format_entry_url(base_url, item[1][0][0][1]),
                }
            # add to the list
            links.append(link)
        # make a letter entry
        entry = {
            'letter': entry[0],
            'links': links
            }
        # result list update
        result.append(entry)

    # return result list
    return result

def get_modentries(base_url, doc_dir):
    """Returns a list of the sphinx modules index entries of the project
    documentation.

    @param base_url: project base url
    @type base_url: str

    @param doc_dir: web documention directory
    @type doc_dir: str
    """
    # get the index pickler object
    # XXX this should be rewritten properly for different domain indices
    # XXX but I'm too lazy for that
    content_pickler = get_pickler(doc_dir, 'py-modindex.fpickle')

    # little check
    if not content_pickler:
        return

    # read pickler
    content = content_pickler['content']

    # result list
    result = list()

    for letter, entries in content:
        # ceate letter entry
        item = dict()
        item['letter'] = letter
        item['links'] = list()

        # append to result
        result.append(item)

        for entry in entries:
            # link dict
            link = {
                'title': entry[0],
                'url': format_entry_url(base_url, '../' + entry[2]),
                }
            # add to the entry
            item['links'].append(link)

    # return result list
    return result

def get_links(base_url, doc_dir):
    """Returns simple list of links to all the document pages found during the
    documentation generation.

    @param base_url: project base url
    @type base_url: str

    @param doc_dir: web documention directory
    @type doc_dir: str
    """
    # get the index pickler object
    menu_pickler = get_pickler(doc_dir, 'searchindex.pickle')

    # little check
    if not menu_pickler:
        return

    # set page links variable
    links = list()
    for index, item in enumerate(menu_pickler[0]):
        title = menu_pickler[1][index].replace('&#8217;', '\'')
        url = '%s?action=view&item=%s' % (base_url, item)
        link = {
            'url': url,
            'title': title
            }
        links.append(link)

    return links
