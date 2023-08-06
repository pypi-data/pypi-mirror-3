# python import
import os

# genshi import
from genshi import XML

## tools import
from sphinx.webtools.pickler_tools import  get_pickler

def highlight(content, words):
    """Tricky function to highlight search result in a page using <a> tag and
    class find. Old fashion parsing way explode the html tags and content and
    rebuild everything at the end with the tags for highlihting.

    @param content: content we want to highlight
    @type content: str

    @param words: words to be highlighted in the content
    @type words: str
    """
    try:
        # resulting content
        content_result = ''
        # first split:
        #   src: <tag>content</tag>
        #   result: ['<tag', 'content</tag', '']
        content_right = content.split('>')
        # work on split right result
        for ct_r in content_right:
            # split left:
            #   src1: ['<tag']
            #   dest1: ['', 'tag']
            #   src2: ['content</tag']
            #   dest2: ['content', '/tag']
            #   src3: ['']
            #   dest3: ['']
            content_left = ct_r.split('<')
            # we observe that we extract:
            #   - the content at : content_left[0]
            #   - the tag at content_left[1]
            # we rebuild the content with the highlight tag now
            if len(content_left) == 2:
                # highlight tag
                content_left[0] = content_left[0].replace(words,
                                    '<a class="find">%s</a>' % words)
                # rebuild
                content_result += content_left[0]
                content_result += '<%s>' % content_left[1]

        # return highlighted content
        return content_result

    except:
        return content

def search_in_file(doc_dir, file, title, words, result):
    """Search words in a source file and update the current result.

    @param doc_dir: web documention directory
    @type doc_dir: str

    @param file: file name base to study
    @type file: str

    @param title: title of the current studied file
    @type type: str

    @param words: list of words to search in the file
    @type words: list

    @param result: current result to update
    @type: dict
    """
    # source file
    file_name = '%s.txt' % file
    file_path = os.path.join(doc_dir, '_sources', file_name)

    # open file for search
    file_ = open(file_path)

    # do search in file
    for line in file_.readlines():
        line = line.lower()
        # line update flag
        update = False
        # if wors find
        if not line.find(words) == -1:
            # reformat line first time
            # already formatted
            if not update:
                line = line.replace('>', '&gt;')
                line = line.replace('<', '&lt;')
                line = '<div>%s</div>\n' % line
            # add word highlight
            line = line.replace(words,
                        '<a class="find" id="find">%s</a>' % words)
            # set flag
            update = True
        # update result
        if update:
            if result.has_key(file):
                #
                result[file]['lines'].append(XML(line))
            else:
                #
                result[file] = {
                    'title': title,
                    'lines': [XML(line)]
                    }

    # close file after search
    file_.close()

def do_search(doc_dir, words):
    """Search first path. Do search in each documentation files using the
    *search_in_file* method.

    @param doc_dir: web documention directory
    @type doc_dir: str

    @param words: list of words to search in the documentation
    @type words: list
    """
    # get the index pickler object
    menu_pickler = get_pickler(doc_dir, 'searchindex.pickle')
    # set page links variable
    links = list()
    # dict words search result
    result = dict()
    # update dict
    for index, file in enumerate(menu_pickler['filenames']):
        # trigger the search in the file
        title = menu_pickler['titles'][index]
        title = title.replace('&#8217;', '\'')
        search_in_file(doc_dir, file, title, words, result)

    # return result
    if len(result) > 0:
        return result
    # None if no result
    else:
        return None

def search(base_url, doc_dir, words):
    """Does search il the source file of the project documentation and format a
    result result for an HTML simple render.

    @param base_url: project base url
    @type base_url: str

    @param doc_dir: web documention directory
    @type doc_dir: str

    @param words: list of words to search in the documentation
    @type words: list
    """
    # buid result
    result_words = do_search(doc_dir, words)

    # nothing if no result
    if not result_words:
        return None

    # list for result
    result = list()

    # reformat result for tg templating render
    for src_key in result_words.keys():
        search_words = words.replace(' ', '+')
        #
        url = '%s?action=view' % base_url
        url += '&item=%s' % src_key
        url += '&search_words=%s' % search_words
        result.append(
                    {
                        'url': url,
                        'title': result_words[src_key]['title'],
                        'lines': result_words[src_key]['lines']
                        }
                    )

    # return the result at the and
    return result
