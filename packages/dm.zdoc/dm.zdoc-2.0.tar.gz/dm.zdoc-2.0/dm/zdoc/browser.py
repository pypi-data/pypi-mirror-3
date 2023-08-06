"""Provide documentation inside a running Zope instance."""
import sys
from pydoc import html, locate, describe, ErrorDuringImport

from Products.Five.browser import BrowserView


class Doc(BrowserView):

  def __before_publishing_traverse__(self, *args):
    r = self.request; path = r.path
    r.set("traverse_subpath", path[:]); del path[:]

  def __call__(self):
    r = self.request
    r.response.setBase(r["URL"])
    path = r.get("traverse_subpath", ())
    if path:
      assert len(path) == 1
      oid = path.pop()
      if oid.endswith(".html"): oid = oid[:-5]
      if oid != ".":
        try: obj = locate(oid, False)
        except ErrorDuringImport, value:
          return html.page(oid, html.escase(str(value)))
        if obj: return html.page(describe(obj), html.document(obj, oid))
        else: return html.page("no Python documentation found for %s" % oid)
    # overall index
    heading = html.heading(
      "<big><strong>Python: Index of Modules</strong></big>",
      "#ffffff", "#7799ee"
      )
    indices = ["<p>" + html.bigsection(
      "Built-in Modules", "#ffffff", "#ee77aa",
      html.multicolumn(
        [name for name in sys.builtin_module_names if name != "__main__"],
        lambda name: '<a href="%s.html">%s</a>' % (name, name)
        )
      )]
    seen = {}
    for dir in sys.path: indices.append(html.index(dir, seen))
    return html.page("Module Index", heading + "".join(indices))
    

