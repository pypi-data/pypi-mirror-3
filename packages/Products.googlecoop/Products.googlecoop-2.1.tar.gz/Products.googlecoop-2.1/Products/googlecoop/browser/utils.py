import urlparse
from Products.CMFPlone.utils import normalizeString

def name_label(label):
    """
    Convert a Word into a google label.
    Labels seem to have to constist solely lowercase letters and _ underscores
    """
    name = normalizeString(label)
    name = name.replace('.','_')
    name = name.replace('-','_')
    while name.find('__')>=0:
        name = name.replace('__', '_')
    return name

def get_label_names(indexes, catalog):
    label_names={}
    for index in indexes:
        values = catalog.uniqueValuesFor(index)
        for value in values:
            label_names[value] = name_label(value)
    return label_names


def extract_labels(brains, indexes, catalog):
    """
    extract the labels out of the results of the query
    -> brains: (searchresults)
    -> indexes: list of attributes to be treated as lables
    -> catalog: portal_catalog
    @return dictionary {'label_name': 'Label Title', ...}
    [{'label_name':'label1', 'label_title': 'Title 1'}, ...]
    """
    label_names = get_label_names(indexes, catalog)
    labels  = {}
    labellist = []
    for brain in brains:
        for index in indexes:
            # assumes a list!
            keywords = getattr(brain, index, [])
            for keyword in keywords:
                labels[label_names[keyword]] = keyword
    for k, v in labels.iteritems():
        labellist.append({'label_name':k, 'label_title':v})
    return labellist

def extract_urls(brains, indexes, catalog):
    """
    extracts urls from the results of a query
    -> brains: (searchresults)
    -> indexes: list of attributes to be treated as lables
    -> catalog: portal_catalog
    @return list of dictionaries urls with labels
    [{'url':'iwlearn.net', 'labels': [label_1, label_2, ...]}, ... ]
    """
    urls = {}
    urllist = []
    label_names = get_label_names(indexes, catalog)
    for brain in brains:
        if brain.getRemoteUrl:
            url = urlparse.urlsplit(brain.getRemoteUrl)
            if url.scheme != '' and url.scheme != 'file':
                domain = url.netloc.lower()
                path = url.path
                labels = urls.get(domain, [])
                for index in indexes:
                    keywords = getattr(brain, index, [])
                    for keyword in keywords:
                        labels.append(label_names[keyword])
                urls[domain] = list(set(labels))
    for k, v in urls.iteritems():
        if k:
            urllist.append({'url':k, 'labels':v})
    return urllist



