__author__ = 'Simon Greenhill <simon@simon.net.nz>'

__version__ = "0.1"
PACKAGE_NAME = "journaltocs"
PACKAGE_VERSION = __version__
VERSION = __version__
PACKAGE_AUTHOR = "Simon Greenhill"
PACKAGE_COPYRIGHT = "Copyright 2012 Simon Greenhill"
PACKAGE_LICENSE = """Copyright (c) 2012, Simon Greenhill <simon@simon.net.nz>
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, 
       this list of conditions and the following disclaimer.
    
    2. Redistributions in binary form must reproduce the above copyright 
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of python-nexus nor the names of its contributors may be
       used to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""

import feedparser
from urllib import quote_plus


class JournalTOCsArgumentException(Exception):
    def __init__(self, arg):
        Exception.__init__(self, "Incorrect Argument: '%s'" % arg)
        self.arg = arg



class JournalTOCsAPI(object):
    BASEURL = 'http://www.journaltocs.ac.uk/api'
    
    def _get(self, url):
        return feedparser.parse(url)
    
    def journal(self, journal_id):
        """
        Returns the journal information for the journal specified by the 
        `journal_id` (Either an ISSN or a JournalTOCs id number).
        
        :param journal_id: journal identifier (id or ISSN)
        :type journal_id: string
        
        :return: dictionary giving journal information
        :rtype: dict
        """
        xml = self._get("%s/journals/%s" % \
            (self.BASEURL, quote_plus(journal_id)))
        return xml.entries
        
    def articles(self, journal_issn):
        """
        Returns the latest articles for the journal specified by the `journal_issn`.
        
        :param journal_issn: journal ISSN identifier
        :type journal_issn: string
        
        :return: dictionary of journal articles
        :rtype: dict
        """
        xml = self._get("%s/journals/%s?output=articles" % \
            (self.BASEURL, quote_plus(journal_issn)))
        return xml.entries
    
    def search_journals(self, query):
        """
        Returns the journal titles matching `query`.
        
        :param query: A search query
        :type query: string
        
        :return: dictionary of journal articles
        :rtype: dict
        """
        xml = self._get("%s/journals/%s" % \
            (self.BASEURL, quote_plus(query)))
        return xml.entries
    
    def search_articles_for_keywords(self, keywords):
        """
        Returns the articles matching keywords in `keywords`.
        
        :param keywords: A list of keywords
        :type keywords: list
        
        :return: dictionary of journal articles
        :rtype: dict
        
        :raises JournalTOCsArgumentException: If the keywords are not a list/tuple.
        """
        if not isinstance(keywords, (list, tuple)):
            raise JournalTOCsArgumentException("Keywords must be a list or tuple")
        xml = self._get("%s/articles/%s" % \
            (self.BASEURL, quote_plus("+".join(keywords))))
        return xml.entries
        
    def search_articles_for_string(self, query):
        """
        Returns the articles matching keywords in `keywords`.
        
        :param query: A search query
        :type query: string
        
        :return: dictionary of journal articles
        :rtype: dict
        """
        xml = self._get("%s/articles/%s" % \
            (self.BASEURL, quote_plus('"%s"' % query)))
        return xml.entries
        
