from contextlib import contextmanager
from core import Docx
import elements

meta = {
    "title": "",
    "subject": "",
    "creator": "",
    "keywords": [],
}

doc = None
def start_doc(**kwargs):
    global doc, meta
    
    if kwargs.get("meta", None) is not None: 
        meta = kwargs['meta']
        
    doc = Docx()
    
### DSL

h_ = lambda level, txt: doc.append(elements.heading(txt, level))
h1 = lambda txt: h_(1, txt)
h2 = lambda txt: h_(2, txt)
h3 = lambda txt: h_(3, txt)
h4 = lambda txt: h_(4, txt)

p = lambda txt: doc.append(elements.paragraph(txt))

br = lambda **kwargs: doc.append(elements.pagebreak(**kwargs))

def img(src, alt=""):
    raise NotImplementedError
    relationships = None
    relationships, picpara = doc.picture(relationships, src, alt)
    doc.append(picpara)

@contextmanager
def ul():
    yield lambda txt: doc.append(elements.paragraph(txt, style='ListBullet'))
        
@contextmanager
def ol():
    yield lambda txt: doc.append(elements.paragraph(txt, style='ListNumber'))

@contextmanager
def table():
    t = []
    
    @contextmanager    
    def tr():
        r = []
        t.append(r)
        yield lambda txt: r.append(txt)
                
    yield tr
    doc.append(elements.table(t, 
        heading=False, 
        borders={"all": {'sz': 2, 'color': 'cccccc'}},
        celstyle=[{'fill': "ffffff"}] * len(t)
    ))
        
## utility functions...
def write_docx(f):
    doc.title = str(meta.get('title', ''))
    doc.subject = str(meta.get('subject', ''))
    doc.creator = str(meta.get('creator', ''))
    doc.keywords = list(meta.get('keywords', []))
       
    doc.save(f)