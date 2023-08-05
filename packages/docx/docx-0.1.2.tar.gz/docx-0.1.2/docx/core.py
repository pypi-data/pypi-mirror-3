# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import os
from os.path import join
import re
import shutil
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from lxml import etree
import dateutil.parser
    
from utils import findTypeParent, dir_to_docx
from metadata import nsprefixes

log = logging.getLogger(__name__)

# Record template directory's location which is just 'template' for a docx
# developer or 'site-packages/docx-template' if you have installed docx
template_dir = join(os.path.dirname(__file__),'docx-template') # installed
if not os.path.isdir(template_dir):
    template_dir = join(os.path.dirname(__file__),'template') # dev

    
class Docx(object):
    trees_and_files = {
        "document": 'word/document.xml',
        "coreprops":'docProps/core.xml',
        "appprops":'docProps/app.xml',
        "contenttypes":'[Content_Types].xml',
        "websettings":'word/webSettings.xml',
        "wordrelationships":'word/_rels/document.xml.rels'
    }
    def __init__(self, f=None):
        create_new_doc = f is None
        self._orig_docx = f
        self._tmp_file = NamedTemporaryFile()
        
        if create_new_doc:
            f = self.__generate_empty_docx()
        
        shutil.copyfile(f, self._tmp_file.name)
        self._docx = ZipFile(self._tmp_file.name, mode='a')
        
        for tree, f in self.trees_and_files.items():
            self._load_etree(tree, f)
            
        self.docbody = self.document.xpath('/w:document/w:body', namespaces=nsprefixes)[0]
        
        if create_new_doc: 
            self.created = datetime.utcnow()
        
    def __new__(cls, *args, **kwargs):
        # Make getters and setter for the core properties
        def set_coreprop_property(prop, to_python=unicode, to_str=unicode):
            getter = lambda self: to_python(self._get_coreprop_val(prop))
            setter = lambda self, val: self._set_coreprop_val(prop, to_str(val))
            setattr(cls, prop, property(getter, setter))
            
        for prop in ['title', 'subject', 'creator', 'description', 
                     'lastModifiedBy', 'revision']:
            set_coreprop_property(prop)
            
        for datetimeprop in ['created', 'modified']:
            set_coreprop_property(datetimeprop, 
                to_python=dateutil.parser.parse,
                to_str=lambda obj: (obj.isoformat() 
                                    if hasattr(obj, 'isoformat') 
                                    else dateutil.parser.parse(obj).isoformat())
            )
        return super(Docx, cls).__new__(cls, *args, **kwargs)
            
    def append(self, *args, **kwargs):
        return self.docbody.append(*args, **kwargs)
    
    def search(self, search):
        '''Search a document for a regex, return success / fail result'''
        document = self.docbody
        
        result = False
        searchre = re.compile(search)
        for element in document.iter():
            if element.tag == '{%s}t' % nsprefixes['w']: # t (text) elements
                if element.text:
                    if searchre.search(element.text):
                        result = True
        return result
    
    def replace(self, search, replace):
        '''Replace all occurences of string with a different string, return updated document'''
        newdocument = self.docbody
        searchre = re.compile(search)
        for element in newdocument.iter():
            if element.tag == '{%s}t' % nsprefixes['w']: # t (text) elements
                if element.text:
                    if searchre.search(element.text):
                        element.text = re.sub(search,replace,element.text)
        return newdocument
    
    def clean(self):
        """ Perform misc cleaning operations on documents.
            Returns cleaned document.
        """
    
        newdocument = self.document
    
        # Clean empty text and r tags
        for t in ('t', 'r'):
            rmlist = []
            for element in newdocument.iter():
                if element.tag == '{%s}%s' % (nsprefixes['w'], t):
                    if not element.text and not len(element):
                        rmlist.append(element)
            for element in rmlist:
                element.getparent().remove(element)
    
        return newdocument
    
    def advanced_replace(self, search, replace, max_blocks=3):
        '''Replace all occurences of string with a different string, return updated document
    
        This is a modified version of python-docx.replace() that takes into
        account blocks of <bs> elements at a time. The replace element can also
        be a string or an xml etree element.
    
        What it does:
        It searches the entire document body for text blocks.
        Then scan thos text blocks for replace.
        Since the text to search could be spawned across multiple text blocks,
        we need to adopt some sort of algorithm to handle this situation.
        The smaller matching group of blocks (up to bs) is then adopted.
        If the matching group has more than one block, blocks other than first
        are cleared and all the replacement text is put on first block.
    
        Examples:
        original text blocks : [ 'Hel', 'lo,', ' world!' ]
        search / replace: 'Hello,' / 'Hi!'
        output blocks : [ 'Hi!', '', ' world!' ]
    
        original text blocks : [ 'Hel', 'lo,', ' world!' ]
        search / replace: 'Hello, world' / 'Hi!'
        output blocks : [ 'Hi!!', '', '' ]
    
        original text blocks : [ 'Hel', 'lo,', ' world!' ]
        search / replace: 'Hel' / 'Hal'
        output blocks : [ 'Hal', 'lo,', ' world!' ]
    
        @param instance  document: The original document
        @param str       search: The text to search for (regexp)
        @param mixed replace: The replacement text or lxml.etree element to
                              append, or a list of etree elements
        @param int       max_blocks: See above
    
        @return instance The document with replacement applied
    
        '''
        # Enables debug output
        DEBUG = False
    
        newdocument = self.docbody
    
        # Compile the search regexp
        searchre = re.compile(search)
    
        # Will match against searchels. Searchels is a list that contains last
        # n text elements found in the document. 1 < n < max_blocks
        searchels = []
    
        for element in newdocument.iter():
            if element.tag == '{%s}t' % nsprefixes['w']: # t (text) elements
                if element.text:
                    # Add this element to searchels
                    searchels.append(element)
                    if len(searchels) > max_blocks:
                        # Is searchels is too long, remove first elements
                        searchels.pop(0)
    
                    # Search all combinations, of searchels, starting from
                    # smaller up to bigger ones
                    # l = search lenght
                    # s = search start
                    # e = element IDs to merge
                    found = False
                    for l in range(1,len(searchels)+1):
                        if found:
                            break
                        #print "slen:", l
                        for s in range(len(searchels)):
                            if found:
                                break
                            if s+l <= len(searchels):
                                e = range(s,s+l)
                                #print "elems:", e
                                txtsearch = ''
                                for k in e:
                                    txtsearch += searchels[k].text
    
                                # Searcs for the text in the whole txtsearch
                                match = searchre.search(txtsearch)
                                if match:
                                    found = True
    
                                    # I've found something :)
                                    if DEBUG:
                                        log.debug("Found element!")
                                        log.debug("Search regexp: %s", searchre.pattern)
                                        log.debug("Requested replacement: %s", replace)
                                        log.debug("Matched text: %s", txtsearch)
                                        log.debug( "Matched text (splitted): %s", map(lambda i:i.text,searchels))
                                        log.debug("Matched at position: %s", match.start())
                                        log.debug( "matched in elements: %s", e)
                                        if isinstance(replace, etree._Element):
                                            log.debug("Will replace with XML CODE")
                                        elif isinstance(replace (list, tuple)):
                                            log.debug("Will replace with LIST OF ELEMENTS")
                                        else:
                                            log.debug("Will replace with:", re.sub(search,replace,txtsearch))
    
                                    curlen = 0
                                    replaced = False
                                    for i in e:
                                        curlen += len(searchels[i].text)
                                        if curlen > match.start() and not replaced:
                                            # The match occurred in THIS element. Puth in the
                                            # whole replaced text
                                            if isinstance(replace, etree._Element):
                                                # Convert to a list and process it later
                                                replace = [ replace, ]
                                            if isinstance(replace, (list,tuple)):
                                                # I'm replacing with a list of etree elements
                                                # clear the text in the tag and append the element after the
                                                # parent paragraph
                                                # (because t elements cannot have childs)
                                                p = findTypeParent(searchels[i], '{%s}p' % nsprefixes['w'])
                                                searchels[i].text = re.sub(search,'',txtsearch)
                                                insindex = p.getparent().index(p) + 1
                                                for r in replace:
                                                    p.getparent().insert(insindex, r)
                                                    insindex += 1
                                            else:
                                                # Replacing with pure text
                                                searchels[i].text = re.sub(search,replace,txtsearch)
                                            replaced = True
                                            log.debug("Replacing in element #: %s", i)
                                        else:
                                            # Clears the other text elements
                                            searchels[i].text = ''
        return newdocument
        
    def _get_etree(self, xmldoc):
        return etree.fromstring(self._docx.read(xmldoc))
        
    def _load_etree(self, name, xmldoc):
        setattr(self, name, self._get_etree(xmldoc))

    def template(self, cx, max_blocks=5, raw_document=False):
        """
        Accepts a context dictionary (cx) and looks for the dict keys wrapped 
        in {{key}}. Replaces occurances with the correspoding value from the
        cx dictionary.
        
        example:
            with the context...
                cx = {
                    'name': 'James',
                    'lang': 'English'
                }
            
            ...and a docx file containing:
                
                Hi! My name is {{name}} and I speak {{lang}}
                
            Calling `docx.template(cx)` will return a new docx instance (the
            original is not modified) that looks like:
            
                Hi! My name is James and I speak English
                
            Note: the template must not have spaces in the curly braces unless
            the dict key does (i.e., `{{ name }}` will not work unless your
            dictionary has `{" name ": ...}`)
                
        The `raw_document` argument accepts a boolean, which (if True) will 
        treat the word/document.xml file as a text template (rather than only 
        replacing text that is visible in the document via a word processor)
        
        If you pass `max_blocks=None` you will cause the template function to
        use `docx.replace()` rather than `docx.advanced_replace()`.
        
        When `max_blocks` is a number, it is passed to the advanced replace
        method as is.   
        """
        output = self.copy()
        
        if raw_document:
            raw_doc = etree.tostring(output.document)
            
        for key, val in cx.items():
            key = "{{%s}}" % key
            if raw_document:
                raw_doc = raw_doc.replace(key, unicode(val))
            elif max_blocks is None: 
                output.replace(key, unicode(val))
            else:                  
                output.advanced_replace(key, val, max_blocks=max_blocks)
            
        if raw_document:
            output.document = etree.fromstring(raw_doc)
            
        return output

    def save(self, dest=None):
        self.modified = datetime.utcnow()
        
        outf = NamedTemporaryFile()
        out_zip = ZipFile(outf.name, mode='w')
        
        orig_contents = self._docx.namelist()
        modified_contents = self.trees_and_files.values()
        
        # Serialize our trees into our zip file
        for tree, dest_file in self.trees_and_files.items():
            log.info('Saving: ' + dest_file)
            out_zip.writestr(dest_file, etree.tostring(getattr(self, tree), pretty_print=True))
        
        for dest_file in set(orig_contents) - set(modified_contents):
            out_zip.writestr(dest_file, self._docx.read(dest_file))
    
        
        # docx file doesn't save properly unless it gets closed
        out_zip.close()
        if dest is not None:
            log.info('Saved new file to: %r', dest)
            shutil.copyfile(outf.name, dest)
            outf.close()
        else:
             
            self._docx.close()
            
            shutil.copyfile(outf.name, self._tmp_file.name)
            
            # reopen the file so it can continue to be used
            self._docx = ZipFile(self._tmp_file.name, mode='a')
            
    def copy(self):
        tmp = NamedTemporaryFile()
        self.save(tmp.name)
        docx = self.__class__(tmp.name)
        docx._orig_docx = self._orig_docx
        tmp.close()
        return docx
    
    def __del__(self):
        try: 
            self.__empty_docx.close()
        except AttributeError: 
            pass
        self._docx.close()
        self._tmp_file.close()
        
    def _get_coreprop(self, tagname):
        return self.coreprops.xpath("*[local-name()='title']")[0]
    
    def _get_coreprop_val(self, tagname):
        return self._get_coreprop(tagname).text
    
    def _set_coreprop_val(self, tagname, val):
        self._get_coreprop(tagname).text = val
        
    def __generate_empty_docx(self):
        self.__empty_docx = NamedTemporaryFile()
        loc = self.__empty_docx.name
        
        dir_to_docx(template_dir, loc)
        
        return loc
    
    @property
    def text(self):
        '''Return the raw text of a document, as a list of paragraphs.'''
        document = self.docbody
        paratextlist = []
        # Compile a list of all paragraph (p) elements
        paralist = []
        for element in document.iter():
            # Find p (paragraph) elements
            if element.tag == '{'+nsprefixes['w']+'}p':
                paralist.append(element)
        # Since a single sentence might be spread over multiple text elements, iterate through each
        # paragraph, appending all text (t) children to that paragraphs text.
        for para in paralist:
            paratext=u''
            # Loop through each paragraph
            for element in para.iter():
                # Find t (text) elements
                if element.tag == '{'+nsprefixes['w']+'}t':
                    if element.text:
                        paratext = paratext+element.text
            # Add our completed paragraph text to the list of paragraph text
            if not len(paratext) == 0:
                paratextlist.append(paratext)
        return paratextlist
