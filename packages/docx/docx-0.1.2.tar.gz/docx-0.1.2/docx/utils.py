# -*- coding: utf-8 -*-
import os
from os.path import join, abspath
from zipfile import ZipFile, ZIP_DEFLATED


def findTypeParent(element, tag):
        """ Finds fist parent of element of the given type
        
        @param object element: etree element
        @param string the tag parent to search for
        
        @return object element: the found parent or None when not found
        """
        
        p = element
        while True:
            p = p.getparent()
            if p.tag == tag:
                return p
        
        # Not found
        return None
    
def dir_to_docx(source_dir, output_loc):
    # make sure the output ends up where we expect it
    output_loc = abspath(output_loc)
    
    # Move into the source_dir
    prev_dir = abspath('.') # save previous working dir
    os.chdir(source_dir)
    
    docxfile = ZipFile(output_loc, mode='w', compression=ZIP_DEFLATED)    

    # Add & compress support files
    files_to_ignore = set(['.DS_Store']) # nuisance from some os's
    for dirpath, dirnames, filenames in os.walk('.'): #@UnusedVariable
        for filename in filenames:
            if filename in files_to_ignore:
                continue
            templatefile = join(dirpath,filename)
            archivename = templatefile[2:]
            docxfile.write(templatefile, archivename)
    docxfile.close()
    
    os.chdir(prev_dir) # restore previous working dir