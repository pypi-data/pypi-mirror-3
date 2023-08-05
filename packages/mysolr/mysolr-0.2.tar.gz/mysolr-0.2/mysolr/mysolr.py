# -*- coding: utf-8 -*-
"""
mysolr.mysolr
~~~~~~~~~~~~~

This module impliments the mysolr Solr class, providing an easy access to
operate with a Solr server.

>>> from mysolr import Solr
>>> solr = Solr('http://myserver:8080/solr')
>>> query = {'q':'*:*', 'rows': 0, 'start': 0, 'facet': 'true', 
             'facet.field': 'province'}
>>> query_response = solr.search(**query)

"""
from mysolr_response import SolrResponse
from urlparse import urljoin
from xml.sax.saxutils import escape

import json
import requests


class Solr:
    """Acts as an easy-to-use interface to Solr."""

    def __init__(self, base_url='http://localhost:8080/solr/'):
        """ Initializes a Solr object. Solr URL is a needed parameter.
        """
        self.base_url = base_url

    def search(self, **kwargs):
        """Queries Solr with the given kwargs and returns a SolrResponse
        object.

        :param **kwargs: Dictionary containing any of the available Solr query
                         parameters described in
                         http://wiki.apache.org/solr/CommonQueryParameters.
                         'q' is a mandatory parameter.

        """
        assert 'q' in kwargs
        kwargs['wt'] = 'python'
        # base_url must be end with /
        if self.base_url[-1] != '/':
            self.base_url += '/'
        response = requests.get(urljoin(self.base_url, 'select'), params=kwargs)
        response.raise_for_status()
        response_object = eval(response.read())
        solr_response = SolrResponse(response_object)
        solr_response.url = response.url
        return solr_response

    def update(self, documents, input_type='xml', commit=True):
        """Sends an update/add message to add the array of hashes(documents) to
        Solr.

        :param documents: A list of solr-compatible documents to index. You
                          should use unicode strings for text/string fields.
        :param input_type: The format which documents are sent. Remember that json
                           is not supported until version 3.
        :param commit: If True, sends a commit message after the operation is
                       executed.

        """
        assert input_type in ['xml', 'json']#,
              #'The given type isn\'t correct. Valid types are "json" and "xml".')

        if input_type == 'xml':
            self._post_xml(_get_add_xml(documents))
        else:
            self._post_json(json.dumps(documents))
        if commit:
            self.commit()

    def delete_by_key(self, identifier, commit=True):
        """Sends an ID delete message to Solr.

        :param commit: If True, sends a commit message after the operation is
                       executed.

        """
        xml = '<delete><id>%s</id></delete>' % (identifier)
        self._post_xml(xml)
        if commit:
            self.commit()

    def delete_by_query(self, query, commit=True):
        """Sends a query delete message to Solr.

        :param commit: If True, sends a commit message after the operation is
                       executed.

        """
        xml = '<delete><query>%s</query></delete>' % (query)
        self._post_xml(xml)
        if commit:
            self.commit()

    def commit(self, wait_flush=True,
               wait_searcher=True, expunge_deletes=False):
        """Sends a commit message to Solr.

        :param wait_flush: Block until index changes are flushed to disk (default is
                           True).
        :param wait_searcher: Block until a new searcher is opened and registered
                              as the main query searcher, making the changes
                              visible (default is True).
        :param expunge_deletes: Merge segments with deletes away (default is False)

        """
        xml = '<commit waitFlush="%s" waitSearcher="%s" expungeDeletes="%s" />' % ('true' if wait_flush else 'false',
                                                                                   'true' if wait_searcher else 'false',
                                                                                   'true' if expunge_deletes else 'false')
        self._post_xml(xml)

    def optimize(self, wait_flush=True, wait_searcher=True, max_segments=1):
        """Sends an optimize message to Solr.

        :param wait_flush: Block until index changes are flushed to disk (default
                           is True)
        :param wait_searcher: Block until a new searcher is opened and registered as
                              the main query searcher, making the changes visible
                              (default is True)
        :param max_segments: Optimizes down to at most this number of segments (default is 1)

        """
        xml = '<optimize waitFlush="%s" waitSearcher="%s" maxSegments="%s" />' % ('true' if wait_flush else 'false',
                                                                                  'true' if wait_searcher else 'false',
                                                                                  max_segments)
        self._post_xml(xml)

    def rollback(self):
        """Sends a rollback message to Solr server."""
        xml = '<rollback />'
        self._post_xml(xml)

    def _post_xml(self, xml):
        """ Sends the xml to Solr server.

        :param xml: XML document to be posted.
        """
        url = urljoin(self.base_url, 'update')
        xml_data = xml.encode('utf-8')
        response = requests.post(url, data=xml_data,
                                 headers={'Content-type': 'text/xml; charset=utf-8',
                                          'Content-Length': "%s" % len(xml_data)})
        response.raise_for_status()

    def _post_json(self, json_doc):
        """ Sends the json to Solr server.

        :param json_doc: JSON document to be posted.
        """
        url = urljoin(self.base_url, 'update/json')
        json_data = json_doc.encode('utf-8')
        response = requests.post(url, data=json_data,
                                 headers={'Content-type': 'application/json; charset=utf-8',
                                          'Content-Length': "%s" % len(json_data)})
        response.raise_for_status()

def _get_add_xml(array_of_hash, overwrite=True):
    """ Creates add XML message to send to Solr based on the array of hashes
    (documents) provided.

    :param overwrite: Newer documents will replace previously added documents
                      with the same uniqueKey (default is True)

    """
    xml = '<add overwrite="%s">' % ('true' if overwrite else 'false')
    for doc_hash in array_of_hash:
        doc = '<doc>'
        for key, value in doc_hash.items():
            if type(value) == type(list()):
                for v in value:
                    if isinstance(v, basestring):
                        v = escape(v)
                    doc = '%s<field name="%s">%s</field>' % (doc, key, v)
            else:
                if isinstance(value, basestring):
                    value = escape(value)
                doc = '%s<field name="%s">%s</field>' % (doc, key, value)
        doc = '%s</doc>' % (doc)
        xml = '%s%s' % (xml, doc)
    xml = '%s</add>' % (xml)
    return xml
