A python wrapper for the JournalTOCs API.
=========================================

See: http://www.journaltocs.ac.uk/develop.php


Using JournalTOCsAPI:

>>> from journaltocs import JournalTOCsAPI
>>> jtocs = JournalTOCsAPI()

Retrieve Journal info by ISSN numbers
-------------------------------------

>>> jtoc.journal('1533-290X')
[{'id': u'http://www.tandfonline.com/loi/wlis/',
  'link': u'http://www.tandfonline.com/loi/wlis/',
  'prism_eissn': u'15332918',
  'prism_issn': u'1533-290X',
  'prism_publicationname': u'Journal of Library & Information Services in Distance Learning',
  'publisher': u'Taylor & Francis',
  'title': u'Journal of Library & Information Services in Distance Learning',
  'title_detail': {'base': u'http://www.journaltocs.ac.uk/api/journals/1533-290X',
  ... # etc 
}]


Search for Journal Name
-----------------------

>>> jtoc.search_journals("Trends in Ecology and Evolution")

[{'dc_identifier': u'',
  'id': u'http://www.sciencedirect.com/science/journal/01695347',
  'link': u'http://www.sciencedirect.com/science/journal/01695347',
  'links': [{'href': u'http://www.sciencedirect.com/science/journal/01695347',
             'rel': u'alternate',
             'type': u'text/html'}],
  'prism_haspart': {'rdf:resource': u'http://www.journaltocs.ac.uk/api/journals/0169-5347?output=articles'},
  'prism_issn': u'0169-5347',
  'prism_publicationname': u'Trends in Ecology & Evolution',
  'publisher': u'Elsevier',
  'publisher_detail': {'name': u'Elsevier'},
  'rights': u'Subscription',
  'rights_detail': {'base': u'http://www.journaltocs.ac.uk/api/journals/Trends+in+Ecology+and+Evolution',
                    'language': None,
                    'type': u'text/plain',
                    'value': u'Subscription'},
  'summary': u'Journal HomePage: http://www.sciencedirect.com/science/journal/01695347<br />\nJournal TOC RSS feeds: http://rss.sciencedirect.com/publication/science/6081<br />\nprintISSN: 0169-5347<br />\njournaltocID: 14067<br />\nPublisher: Elsevier<br />\nSubjects: ENVIRONMENTAL STUDIES',
  'summary_detail': {'base': u'http://www.journaltocs.ac.uk/api/journals/Trends+in+Ecology+and+Evolution',
                     'language': None,
                     'type': u'text/html',
                     'value': u'Journal HomePage: http://www.sciencedirect.com/science/journal/01695347<br />\nJournal TOC RSS feeds: http://rss.sciencedirect.com/publication/science/6081<br />\nprintISSN: 0169-5347<br />\njournaltocID: 14067<br />\nPublisher: Elsevier<br />\nSubjects: ENVIRONMENTAL STUDIES'},
  'tags': [{'label': None, 'scheme': None, 'term': u'ENVIRONMENTAL STUDIES'}],
  'title': u'Trends in Ecology & Evolution',
  'title_detail': {'base': u'http://www.journaltocs.ac.uk/api/journals/Trends+in+Ecology+and+Evolution',
                   'language': None,
                   'type': u'text/plain',
                   'value': u'Trends in Ecology & Evolution'}}]

Get Articles for a journal
--------------------------

>>> jtocs.articles("1533-290X")

[{'content': [{'base': u'http://www.journaltocs.ac.uk/api/journals/0169-5347?output=articles',
              'language': None,
              'type': u'text/html',
              'value': u'<p><a href="http://www.sciencedirect.com/science?_ob=GatewayURL&amp;_origin=IRSSCONTENT&amp;_method=citationSearch&amp;_piikey=S0169534712000262&amp;_version=1&amp;md5=14a1b6d3fc9a98e69361aa4a9cb7f94d"><b>The terminology of metacommunity ecology</b></a><br /> <br /><i>Trends in Ecology &amp; Evolution, Vol. , No.  (2012) pp.  - </i><br />Publication year: 2012\nSource: Trends in Ecology &amp; Evolution, Available online 9 February 2012\nAmanda K.&#160;Winegardner, Brittany K.&#160;Jones, Ingrid S.Y.&#160;Ng, Tadeu&#160;Siqueira, Karl&#160;Cottenie</p>'}],
 'dc_identifier': u'http://www.sciencedirect.com/science?_ob=GatewayURL&_origin=IRSSCONTENT&_method=citationSearch&_piikey=S0169534712000262&_version=1&md5=14a1b6d3fc9a98e69361aa4a9cb7f94d',
 'dc_source': u'Trends in Ecology & Evolution, Vol. , No.  (2012) pp.  -',
 'id': u'http://www.sciencedirect.com/science?_ob=GatewayURL&_origin=IRSSCONTENT&_method=citationSearch&_piikey=S0169534712000262&_version=1&md5=14a1b6d3fc9a98e69361aa4a9cb7f94d',
 'link': u'http://www.sciencedirect.com/science?_ob=GatewayURL&_origin=IRSSCONTENT&_method=citationSearch&_piikey=S0169534712000262&_version=1&md5=14a1b6d3fc9a98e69361aa4a9cb7f94d',
 'links': [{'href': u'http://www.sciencedirect.com/science?_ob=GatewayURL&_origin=IRSSCONTENT&_method=citationSearch&_piikey=S0169534712000262&_version=1&md5=14a1b6d3fc9a98e69361aa4a9cb7f94d',
            'rel': u'alternate',
            'type': u'text/html'}],
 'prism_publicationdate': u'2012-02-11T22:28:46Z',
 'prism_publicationname': u'Trends in Ecology & Evolution',
 'publisher': u'Elsevier',
 'publisher_detail': {'name': u'Elsevier'},
 'summary': u'Publication year: 2012<br />\nSource: Trends in Ecology & Evolution, Available online 9 February 2012<br />\nAmanda K.\xa0Winegardner, Brittany K.\xa0Jones, Ingrid S.Y.\xa0Ng, Tadeu\xa0Siqueira, Karl\xa0Cottenie',
 'summary_detail': {'base': u'http://www.journaltocs.ac.uk/api/journals/0169-5347?output=articles',
                    'language': None,
                    'type': u'text/html',
                    'value': u'Publication year: 2012<br />\nSource: Trends in Ecology & Evolution, Available online 9 February 2012<br />\nAmanda K.\xa0Winegardner, Brittany K.\xa0Jones, Ingrid S.Y.\xa0Ng, Tadeu\xa0Siqueira, Karl\xa0Cottenie'},
 'title': u'The terminology of metacommunity ecology',
 'title_detail': {'base': u'http://www.journaltocs.ac.uk/api/journals/0169-5347?output=articles',
                  'language': None,
                  'type': u'text/plain',
                  'value': u'The terminology of metacommunity ecology'},
 'updated': u'2012-02-11T22:28:46Z',
 'updated_parsed': time.struct_time(tm_year=2012, tm_mon=2, tm_mday=11, tm_hour=22, tm_min=28, tm_sec=46, tm_wday=5, tm_yday=42, tm_isdst=0)}
 # ... etc
]

Searching Articles
------------------

By Keyword:

>>> jtocs.search_articles_for_keywords(['a', 'list', 'of', 'keyword'])

By String:

>>> jtocs.search_articles_for_string("Hello world")
