#
# Jasy - Web Tooling Framework
# Copyright 2010-2012 Zynga Inc.
#

import re
from jasy.core.Logging import warn

__all__ = ["extractSummary"]

# Used to filter first paragraph from HTML
paragraphExtract = re.compile(r"^(.*?)(\. |\? |\! |$)")
newlineMatcher = re.compile(r"\n")

# Used to remove markup sequences after doc processing of comment text
stripMarkup = re.compile(r"<.*?>")

def extractSummary(text):
    try:
        text = stripMarkup.sub("", newlineMatcher.sub(" ", text))
        matched = paragraphExtract.match(text)
    except TypeError:
        matched = None
        
    if matched:
        summary = matched.group(1)
        if summary is not None:
            if not summary.endswith((".", "!", "?")):
                summary = summary.strip() + "."
            return summary
            
    else:
        warn("Unable to extract summary for: %s", text)
    
    return None
    
