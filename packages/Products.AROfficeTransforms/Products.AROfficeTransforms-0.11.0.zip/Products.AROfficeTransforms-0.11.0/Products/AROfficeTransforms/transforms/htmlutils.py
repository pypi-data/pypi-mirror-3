
import re

rexCollection=[
  ('((left|top|right|bottom)[ \t]*:[ \t]*[0-9]+)[ \t]*([;"])', r"\1px\3" )
]

rexColl=[]
for rex, subtxt in rexCollection:
  rexColl.append((re.compile(rex), subtxt))

del rexCollection

def fixBrokenStyles(html):
  for rex, subtxt in rexColl:
    html = rex.sub(subtxt, html)
  return html
