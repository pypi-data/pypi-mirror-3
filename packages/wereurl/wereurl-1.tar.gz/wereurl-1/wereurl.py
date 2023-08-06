# -*- coding: iso-8859-15 -*-
import re

# regex provided by John Gruber (http://daringfireball.net/2010/07/improved_regex_for_matching_urls)
RE_URL = re.compile("""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")

def search(text):
	return [match.groups()[0] for match in RE_URL.finditer(text)]
