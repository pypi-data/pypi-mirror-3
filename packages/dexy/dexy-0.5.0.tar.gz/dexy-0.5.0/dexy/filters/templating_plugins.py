from ordereddict import OrderedDict
from pygments.styles import get_all_styles
import json
import os
import pprint
import pygments
import pygments.formatters
import re
import urllib

class TemplatePlugin(object):
    def __init__(self, filter_instance):
        self.filter_instance = filter_instance

    def run(self):
        return {}

class PrettyPrinterTemplatePlugin(TemplatePlugin):
    def run(self):
        return { 'pformat' : pprint.pformat}

class RegularExpressionsTemplatePlugin(TemplatePlugin):
    def run(self):
        return { 're_match' : re.match, 're_search' : re.search}

class PythonBuiltinsTemplatePlugin(TemplatePlugin):
    # Intended to be all builtins that make sense to run within a document.
    PYTHON_BUILTINS = [abs, all, any, bin, bool, bytearray, callable, chr,
        cmp, complex, dict, dir, divmod, enumerate, filter, float, format,
        hex, id, int, isinstance, issubclass, iter, len, list, long, map,
        max, min, oct, ord, pow, range, reduce, repr, reversed, round,
        set, slice, sorted, str, sum, tuple, xrange, zip]

    def run(self):
        return dict((f.__name__, f) for f in self.PYTHON_BUILTINS)

class PygmentsStylesheetTemplatePlugin(TemplatePlugin):
    def run(self):
        pygments_stylesheets = {}
        for style_name in get_all_styles():
            for formatter_class in [pygments.formatters.LatexFormatter, pygments.formatters.HtmlFormatter]:
                pygments_formatter = formatter_class(style=style_name)
                style_info = pygments_formatter.get_style_defs()

                for fn in pygments_formatter.filenames:
                    ext = fn.split(".")[1]
                    if ext == 'htm':
                        ext = 'css' # swap the more intuitive '.css' for the unlikely '.htm'
                    key = "%s.%s" % (style_name, ext)
                    pygments_stylesheets[key] = style_info
        return {'pygments' : pygments_stylesheets}

class SubdirectoriesTemplatePlugin(TemplatePlugin):
    def run(self):
        # The directory containing the document to be processed.
        doc_dir = os.path.dirname(self.filter_instance.artifact.name)

        # Get a list of subdirectories under this document's directory.
        subdirectories = [d for d in os.listdir(os.path.join(os.curdir, doc_dir)) if os.path.isdir(os.path.join(os.curdir, doc_dir, d))]
        return {'subdirectories' : subdirectories}

class VariablesTemplatePlugin(TemplatePlugin):
    def run(self):
        if self.filter_instance.artifact.args.has_key('variables'):
            return self.filter_instance.artifact.args['variables']
        else:
            return {}

class GlobalsTemplatePlugin(TemplatePlugin):
    def run(self):
        if self.filter_instance.artifact.controller_args.has_key('globals'):
            return self.filter_instance.artifact.controller_args['globals']
        else:
            return {}

class InputsTemplatePlugin(TemplatePlugin):
    def load_sort_json_data(self, a):
        try:
            unsorted_json = json.loads(a.output_text())
        except ValueError as e:
            print "unable to load JSON for", a.key
            raise e

        def sort_dict(d):
            od = OrderedDict()
            for k in sorted(d.keys()):
                v = d[k]
                if isinstance(v, dict) or isinstance(v, OrderedDict):
                    od[k] = sort_dict(v)
                else:
                    od[k] = v
            return od

        return sort_dict(unsorted_json)

    def run(self):
        d_hash = {}
        a_hash = {}

        name = self.filter_instance.artifact.name
        inputs = self.filter_instance.artifact.inputs()

        for key, a in inputs.iteritems():
            keys = a.relative_refs(name)

            # Do any special handling of data
            if a.ext == '.json':
                data = self.load_sort_json_data(a)
            else:
                data = a.data_dict

            for k in keys:
                # Avoid adding duplicate keys
                if a_hash.has_key(k):
                    next

                a_hash[k] = a

                if data.keys() == ['1']:
                    d_hash[k] = data['1']
                else:
                    d_hash[k] = data

        return {
            'a' : a_hash,
            's' : self.filter_instance.artifact,
            'd' : d_hash,
            'f' : self,
        }

class ClippyHelperTemplatePlugin(TemplatePlugin):
    PRE_AND_CLIPPY_STRING = """
<pre>
%s
</pre>%s
    """
    CLIPPY_HELPER_STRING = """
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
                width="110"
                height="14"
                id="clippy" >
<param name="movie" value="/clippy.swf"/>
<param name="allowScriptAccess" value="always" />
<param name="quality" value="high" />
<param name="scale" value="noscale" />
<param NAME="FlashVars" value="text=%s">
<param name="bgcolor" value="#ffffff">
<embed src="/clippy.swf"
       width="110"
       height="14"
       name="clippy"
       quality="high"
       allowScriptAccess="always"
       type="application/x-shockwave-flash"
       pluginspage="http://www.macromedia.com/go/getflashplayer"
       FlashVars="text=%s"
       bgcolor="#ffffff"
/>
</object>"""

    def run(self):
        return {
            'pre_and_clippy' : self.pre_and_clippy,
            'clippy_helper' : self.clippy_helper
        }

    def pre_and_clippy(self, text):
        return self.PRE_AND_CLIPPY_STRING % (text, self.clippy_helper(text))

    def clippy_helper(self, text):
        if not text or len(text) == 0:
            raise Exception("You passed blank text to clippy helper!")
        quoted_text = urllib.quote(text)
        return self.CLIPPY_HELPER_STRING % (quoted_text, quoted_text)
