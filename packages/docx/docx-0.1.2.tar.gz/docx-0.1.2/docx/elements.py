# -*- coding: utf-8 -*-
import os
from os.path import join
import shutil

from lxml import etree
try:
    from PIL import Image
except ImportError:
    import Image
    
from metadata import TEMPLATE_DIR, nsprefixes

def Element(tagname, tagtext=None, nsprefix='w', attributes=None,attrnsprefix=None):
    '''Create an element & return it'''
    # Deal with list of nsprefix by making namespacemap
    namespacemap = None
    if isinstance(nsprefix, list):
        namespacemap = {}
        for prefix in nsprefix:
            namespacemap[prefix] = nsprefixes[prefix]
        nsprefix = nsprefix[0] # FIXME: rest of code below expects a single prefix
    if nsprefix:
        namespace = '{'+nsprefixes[nsprefix]+'}'
    else:
        # For when namespace = None
        namespace = ''
    newelement = etree.Element(namespace+tagname, nsmap=namespacemap)
    # Add attributes with namespaces
    if attributes:
        # If they haven't bothered setting attribute namespace, use an empty string
        # (equivalent of no namespace)
        if not attrnsprefix:
            # Quick hack: it seems every element that has a 'w' nsprefix for its tag uses the same prefix for it's attributes
            if nsprefix == 'w':
                attributenamespace = namespace
            else:
                attributenamespace = ''
        else:
            attributenamespace = '{'+nsprefixes[attrnsprefix]+'}'

        for tagattribute in attributes:
            newelement.set(attributenamespace+tagattribute, attributes[tagattribute])
    if tagtext:
        newelement.text = tagtext
    return newelement


def pagebreak(breaktype='page', orient='portrait'):
    '''Insert a break, default 'page'.
    See http://openxmldeveloper.org/forums/thread/4075.aspx
    Return our page break element.'''
    # Need to enumerate different types of page breaks.
    validtypes = ['page', 'section']
    if breaktype not in validtypes:
        raise ValueError('Page break style "%s" not implemented. Valid styles: %s.' % (breaktype, validtypes))
    pagebreak = Element('p')
    if breaktype == 'page':
        run = Element('r')
        br = Element('br',attributes={'type':breaktype})
        run.append(br)
        pagebreak.append(run)
    elif breaktype == 'section':
        pPr = Element('pPr')
        sectPr = Element('sectPr')
        if orient == 'portrait':
            pgSz = Element('pgSz',attributes={'w':'12240','h':'15840'})
        elif orient == 'landscape':
            pgSz = Element('pgSz',attributes={'h':'12240','w':'15840', 'orient':'landscape'})
        sectPr.append(pgSz)
        pPr.append(sectPr)
        pagebreak.append(pPr)
    return pagebreak

def paragraph(paratext,style='BodyText',breakbefore=False,jc='left'):
    '''Make a new paragraph element, containing a run, and some text.
    Return the paragraph element.

    @param string jc: Paragraph alignment, possible values:
                      left, center, right, both (justified), ...
                      see http://www.schemacentral.com/sc/ooxml/t-w_ST_Jc.html
                      for a full list

    If paratext is a list, spawn multiple run/text elements.
    Support text styles (paratext must then be a list of lists in the form
    <text> / <style>. Stile is a string containing a combination od 'bui' chars

    example
    paratext = [
        ('some bold text', 'b'),
        ('some normal text', ''),
        ('some italic underlined text', 'iu'),
    ]

    '''
    # Make our elements
    paragraph = Element('p')

    if isinstance(paratext, list):
        text = []
        for pt in paratext:
            if isinstance(pt, (list,tuple)):
                text.append([Element('t',tagtext=pt[0]), pt[1]])
            else:
                text.append([Element('t',tagtext=pt), ''])
    else:
        text = [[Element('t',tagtext=paratext),''],]
    pPr = Element('pPr')
    pStyle = Element('pStyle',attributes={'val':style})
    pJc = Element('jc',attributes={'val':jc})
    pPr.append(pStyle)
    pPr.append(pJc)

    # Add the text the run, and the run to the paragraph
    paragraph.append(pPr)
    for t in text:
        run = Element('r')
        rPr = Element('rPr')
        # Apply styles
        if t[1].find('b') > -1:
            b = Element('b')
            rPr.append(b)
        if t[1].find('u') > -1:
            u = Element('u',attributes={'val':'single'})
            rPr.append(u)
        if t[1].find('i') > -1:
            i = Element('i')
            rPr.append(i)
        run.append(rPr)
        # Insert lastRenderedPageBreak for assistive technologies like
        # document narrators to know when a page break occurred.
        if breakbefore:
            lastRenderedPageBreak = Element('lastRenderedPageBreak')
            run.append(lastRenderedPageBreak)
        run.append(t[0])
        paragraph.append(run)
    # Return the combined paragraph
    return paragraph

def heading(headingtext,headinglevel,lang='en'):
    '''Make a new heading, return the heading element'''
    lmap = {
        'en': 'Heading',
        'it': 'Titolo',
    }
    # Make our elements
    paragraph = Element('p')
    pr = Element('pPr')
    pStyle = Element('pStyle',attributes={'val':lmap[lang]+str(headinglevel)})
    run = Element('r')
    text = Element('t',tagtext=headingtext)
    # Add the text the run, and the run to the paragraph
    pr.append(pStyle)
    run.append(text)
    paragraph.append(pr)
    paragraph.append(run)
    # Return the combined paragraph
    return paragraph

def table(contents, heading=True, colw=None, cwunit='dxa', tblw=0, twunit='auto', borders={}, celstyle=None):
    '''Get a list of lists, return a table

        @param list contents: A list of lists describing contents
                              Every item in the list can be a string or a valid
                              XML element itself. It can also be a list. In that case
                              all the listed elements will be merged into the cell.
        @param bool heading: Tells whether first line should be threated as heading
                             or not
        @param list colw: A list of interger. The list must have same element
                          count of content lines. Specify column Widths in
                          wunitS
        @param string cwunit: Unit user for column width:
                                'pct': fifties of a percent
                                'dxa': twenties of a point
                                'nil': no width
                                'auto': automagically determined
        @param int tblw: Table width
        @param int twunit: Unit used for table width. Same as cwunit
        @param dict borders: Dictionary defining table border. Supported keys are:
                             'top', 'left', 'bottom', 'right', 'insideH', 'insideV', 'all'
                             When specified, the 'all' key has precedence over others.
                             Each key must define a dict of border attributes:
                             color: The color of the border, in hex or 'auto'
                             space: The space, measured in points
                             sz: The size of the border, in eights of a point
                             val: The style of the border, see http://www.schemacentral.com/sc/ooxml/t-w_ST_Border.htm
        @param list celstyle: Specify the style for each colum, list of dicts.
                              supported keys:
                              'align': specify the alignment, see paragraph documentation,

        @return lxml.etree: Generated XML etree element
    '''
    table = Element('tbl')
    columns = len(contents[0])
    # Table properties
    tableprops = Element('tblPr')
    tablestyle = Element('tblStyle',attributes={'val':'ColorfulGrid-Accent1'})
    tableprops.append(tablestyle)
    tablewidth = Element('tblW',attributes={'w':str(tblw),'type':str(twunit)})
    tableprops.append(tablewidth)
    if len(borders.keys()):
        tableborders = Element('tblBorders')
        for b in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            if b in borders.keys() or 'all' in borders.keys():
                k = 'all' if 'all' in borders.keys() else b
                attrs = {}
                for a in borders[k].keys():
                    attrs[a] = unicode(borders[k][a])
                borderelem = Element(b,attributes=attrs)
                tableborders.append(borderelem)
        tableprops.append(tableborders)
    tablelook = Element('tblLook',attributes={'val':'0400'})
    tableprops.append(tablelook)
    table.append(tableprops)
    # Table Grid
    tablegrid = Element('tblGrid')
    for i in range(columns):
        tablegrid.append(Element('gridCol',attributes={'w':str(colw[i]) if colw else '2390'}))
    table.append(tablegrid)
    # Heading Row
    row = Element('tr')
    rowprops = Element('trPr')
    cnfStyle = Element('cnfStyle',attributes={'val':'000000100000'})
    rowprops.append(cnfStyle)
    row.append(rowprops)
    if heading:
        i = 0
        for heading in contents[0]:
            cell = Element('tc')
            # Cell properties
            cellprops = Element('tcPr')
            if colw:
                wattr = {'w':str(colw[i]),'type':cwunit}
            else:
                wattr = {'w':'0','type':'auto'}
            cellwidth = Element('tcW',attributes=wattr)
            cellstyle = Element('shd',attributes={'val':'clear','color':'auto','fill':'548DD4','themeFill':'text2','themeFillTint':'99'})
            cellprops.append(cellwidth)
            cellprops.append(cellstyle)
            cell.append(cellprops)
            # Paragraph (Content)
            if not isinstance(heading, (list, tuple)):
                heading = [heading,]
            for h in heading:
                if isinstance(h, etree._Element):
                    cell.append(h)
                else:
                    cell.append(paragraph(h,jc='center'))
            row.append(cell)
            i += 1
        table.append(row)
    # Contents Rows
    for contentrow in contents[1 if heading else 0:]:
        row = Element('tr')
        i = 0
        for content in contentrow:
            cell = Element('tc')
            # Properties
            cellprops = Element('tcPr')
            if colw:
                wattr = {'w':str(colw[i]),'type':cwunit}
            else:
                wattr = {'w':'0','type':'auto'}
            cellwidth = Element('tcW',attributes=wattr)
            cellprops.append(cellwidth)
            cell.append(cellprops)
            # Paragraph (Content)
            if not isinstance(content, (list, tuple)):
                content = [content,]
            for c in content:
                if isinstance(c, etree._Element):
                    cell.append(c)
                else:
                    if celstyle and 'align' in celstyle[i].keys():
                        align = celstyle[i]['align']
                    else:
                        align = 'left'
                    cell.append(paragraph(c,jc=align))
            row.append(cell)
            i += 1
        table.append(row)
    return table

def picture(relationshiplist, picname, picdescription, pixelwidth=None,
            pixelheight=None, nochangeaspect=True, nochangearrowheads=True):
    '''Take a relationshiplist, picture file name, and return a paragraph containing the image
    and an updated relationshiplist'''
    # http://openxmldeveloper.org/articles/462.aspx
    # Create an image. Size may be specified, otherwise it will based on the
    # pixel size of image. Return a paragraph containing the picture'''
    # Copy the file into the media dir
    media_dir = join(TEMPLATE_DIR,'word','media')
    if not os.path.isdir(media_dir):
        os.mkdir(media_dir)
    shutil.copyfile(picname, join(media_dir,picname))

    # Check if the user has specified a size
    if not pixelwidth or not pixelheight:
        # If not, get info from the picture itself
        pixelwidth,pixelheight = Image.open(picname).size[0:2]

    # OpenXML measures on-screen objects in English Metric Units
    # 1cm = 36000 EMUs
    emuperpixel = 12667
    width = str(pixelwidth * emuperpixel)
    height = str(pixelheight * emuperpixel)

    # Set relationship ID to the first available
    picid = '2'
    picrelid = 'rId'+str(len(relationshiplist)+1)
    relationshiplist.append([
        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
        'media/'+picname])

    # There are 3 main elements inside a picture
    # 1. The Blipfill - specifies how the image fills the picture area (stretch, tile, etc.)
    blipfill = Element('blipFill',nsprefix='pic')
    blipfill.append(Element('blip',nsprefix='a',attrnsprefix='r',attributes={'embed':picrelid}))
    stretch = Element('stretch',nsprefix='a')
    stretch.append(Element('fillRect',nsprefix='a'))
    blipfill.append(Element('srcRect',nsprefix='a'))
    blipfill.append(stretch)

    # 2. The non visual picture properties
    nvpicpr = Element('nvPicPr',nsprefix='pic')
    cnvpr = Element('cNvPr',nsprefix='pic',
                        attributes={'id':'0','name':'Picture 1','descr':picname})
    nvpicpr.append(cnvpr)
    cnvpicpr = Element('cNvPicPr',nsprefix='pic')
    cnvpicpr.append(Element('picLocks', nsprefix='a',
                    attributes={'noChangeAspect':str(int(nochangeaspect)),
                    'noChangeArrowheads':str(int(nochangearrowheads))}))
    nvpicpr.append(cnvpicpr)

    # 3. The Shape properties
    sppr = Element('spPr',nsprefix='pic',attributes={'bwMode':'auto'})
    xfrm = Element('xfrm',nsprefix='a')
    xfrm.append(Element('off',nsprefix='a',attributes={'x':'0','y':'0'}))
    xfrm.append(Element('ext',nsprefix='a',attributes={'cx':width,'cy':height}))
    prstgeom = Element('prstGeom',nsprefix='a',attributes={'prst':'rect'})
    prstgeom.append(Element('avLst',nsprefix='a'))
    sppr.append(xfrm)
    sppr.append(prstgeom)

    # Add our 3 parts to the picture element
    pic = Element('pic',nsprefix='pic')
    pic.append(nvpicpr)
    pic.append(blipfill)
    pic.append(sppr)

    # Now make the supporting elements
    # The following sequence is just: make element, then add its children
    graphicdata = Element('graphicData',nsprefix='a',
        attributes={'uri':'http://schemas.openxmlformats.org/drawingml/2006/picture'})
    graphicdata.append(pic)
    graphic = Element('graphic',nsprefix='a')
    graphic.append(graphicdata)

    framelocks = Element('graphicFrameLocks',nsprefix='a',attributes={'noChangeAspect':'1'})
    framepr = Element('cNvGraphicFramePr',nsprefix='wp')
    framepr.append(framelocks)
    docpr = Element('docPr',nsprefix='wp',
        attributes={'id':picid,'name':'Picture 1','descr':picdescription})
    effectextent = Element('effectExtent',nsprefix='wp',
        attributes={'l':'25400','t':'0','r':'0','b':'0'})
    extent = Element('extent',nsprefix='wp',attributes={'cx':width,'cy':height})
    inline = Element('inline',
        attributes={'distT':"0",'distB':"0",'distL':"0",'distR':"0"},nsprefix='wp')
    inline.append(extent)
    inline.append(effectextent)
    inline.append(docpr)
    inline.append(framepr)
    inline.append(graphic)
    drawing = Element('drawing')
    drawing.append(inline)
    run = Element('r')
    run.append(drawing)
    paragraph = Element('p')
    paragraph.append(run)
    return relationshiplist,paragraph

