#!/usr/bin/env python3 

# Requires feedparser, https://pypi.python.org/pypi/feedparser
# can be installed by pip

import feedparser

feed = feedparser.parse("http://feeds.feedburner.com/quotationspage/qotd")

quote = feed['entries'][0]['summary']

print(quote)
