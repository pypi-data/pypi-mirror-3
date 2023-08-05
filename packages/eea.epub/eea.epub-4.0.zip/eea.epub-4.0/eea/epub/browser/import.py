""" Browser Import
"""

from BeautifulSoup import BeautifulSoup
from Products.Five import BrowserView
from eea.epub.interfaces import IImportedBook
from eea.epub.interfaces import IImportedChapter
from eea.epub.interfaces import IImportedImage
import xml.etree.cElementTree as ET
from persistent.dict import PersistentDict
from zipfile import ZipFile
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
import logging
import re
import transaction
import urllib
import lxml.html

logger = logging.getLogger('eea.epub.browser.import')


def titleToId(title):
    """ Return a stripped title to be made into an id
    """
    return title.strip().strip('!@#$%^&*()<>./+').lower().replace(' ', '-')


def elemTagWithoutNamespace(elem):
    """Remove the xmlns that ElementTree inserts before the tag name

    If a namespace is present, ElementTree prefixes the tag names in
    'Clark's Notation', e.g. {http://www.w3.org/2005/Atom}feed. To make it
    easier to select by tag, we remove this.

    http://stackoverflow.com/questions/1249876
    """
    assert not isinstance(elem, str), \
        'Make sure you pass in the element, not the tag'
    if '}' in elem.tag:
        return elem.tag.split('}')[1]
    return elem.tag


def stripNamespaces(node):
    """ Strips Namespaces from xml elements
    """
    node.tag = elemTagWithoutNamespace(node)
    for elem in node.getchildren():
        elem.tag = elemTagWithoutNamespace(elem)
        stripNamespaces(elem)
    return node

def cleanNames(name):
    """ Remove non alpha numeric characters from argument minus exceptions """
    return "".join(
        (x if (x.isalnum() or x in ['.', '/', '-']) else '_') for x in name)

class EpubFile(object):
    """ EpubFile
    """
    def __init__(self, zipFile):
        self.zipFile = zipFile
        self.cache = {}

    @property
    def rootFile(self):
        """ Find root of the Epub
        """
        if 'rootFile' in self.cache:
            return self.cache['rootFile']

        rfile = self.zipFile.read('META-INF/container.xml')
        xml = ET.XML(rfile)
        xml = stripNamespaces(xml)
        xml = xml.find('rootfiles')
        xml = xml.find('rootfile')
        rootFilePath = xml.get('full-path')
        fileContent = self.zipFile.read(rootFilePath)
        xml = ET.XML(fileContent)
        xml = stripNamespaces(xml)

        self.cache['rootFile'] = xml
        return xml

    @property
    def tocNavPoints(self):
        """ Navigation for table of contents
        """
        filePath = 'OEBPS/toc.ncx'
        fileContent = self.zipFile.read(filePath)
        xml = ET.XML(fileContent)
        xml = stripNamespaces(xml)
        ret = []
        for elem in xml.find('navMap'):
            ret.append({
                'label': elem.find('navLabel').find('text').text,
                'href': elem.find('content').get('src'),
            })
        return ret

    @property
    def coverImageData(self):
        """ Gets the cover image of the epub
        """
        if 'coverImageData' in self.cache:
            return self.cache['coverImageData']

        for elem in self.rootFile.find('manifest').findall('item'):
            mtype = elem.get('media-type', '')
            name = elem.get('type', '')
            mid = elem.get('id', '')
            if mtype.startswith('image') and (name.startswith('cover')
                                             or mid.startswith('cover')):
                coverImageData = self.zipFile.read('OEBPS/' + elem.get('href'))
                self.cache['coverImageData'] = coverImageData
                return coverImageData

        return None

    @property
    def title(self):
        """ Title of the epub
        """
        xml = self.rootFile
        xml = xml.find('metadata')
        xml = xml.find('title')
        return xml.text

    @property
    def page_resources(self):
        """ Defines the epub page resources
        """
        if 'page_resources' in self.cache:
            return self.cache['page_resources']

        guide = self.rootFile.find('guide')
        chapter_hrefs = []
        if guide != None:
            for elem in guide.findall('reference'):
                if elem.get('type') == 'text':
                    chapter_hrefs.append(elem.get('href'))

        page_resources = []
        for elem in self.rootFile.find('manifest').findall('item'):
            if not elem.get('media-type') == 'application/xhtml+xml':
                continue
            href = elem.get('href')
            fileName = 'OEBPS/' + elem.get('href')
            fileContent = self.zipFile.read(fileName)
            html = lxml.html.fromstring(fileContent)
            html = html.find('body')
            isChapter = href in chapter_hrefs
            title = href
            description = ''
            if isChapter:
                description = html.find('p')
                html.remove(description)
                description = description.text.strip()
                h1 = html.find('h1')
                if h1 != None:
                    title = h1.text
                    html.remove(h1)
            imgs = list(html.getiterator('img'))
            for img in imgs:
                img.attrib['src'] = cleanNames(img.attrib['src'])
            ##### regex replace of <a /> with <a></a>
            html = lxml.html.tostring(html)

            def repl(m):
                """ Replace """
                res = m.group(1) + '></a>'
                return res
            regex = r'(<a[^>]*)(/>)'

            html = re.sub(regex, repl, html)
            html = str(BeautifulSoup(html))

            page_resources.append({
                'id': elem.get('href'),
                'title': title,
                'content': html,
                'description': description,
                'isChapter': isChapter,
            })
        self.cache['page_resources'] = page_resources
        return page_resources

    def findDeep(self, elem, href):
        """ Find children in given element
        """
        for child in elem.getchildren():
            if (child.tag == 'img') and (child.get('src') == href):
                return child
            match = self.findDeep(child, href)
            if match != None:
                return match

    def findFirstImageMatchingHref(self, href):
        """ Finds the first image matching the given href
        """
        chapters = [resource for resource in self.page_resources if
                    resource['isChapter']]
        for chapter in chapters:
            body = chapter['content']
            if href in body:
                xml = ET.XML(body)
                xml = stripNamespaces(xml)
                match = None
                for elem in xml.getchildren():
                    match = self.findDeep(elem, href)
                    if match != None:
                        return {
                            'title': match.get('title', ''),
                            'alt': match.get('alt', ''),
                        }
        return {
            'title': '',
            'alt': '',
        }

    @property
    def images(self):
        """ Returns the images of the epub
        """
        if not 'images' in self.cache:
            self.cache['images'] = []
            for elem in self.rootFile.find('manifest').getchildren():
                if elem.get('media-type').startswith('image'):
                    href = elem.get('href')
                    firstMatch = self.findFirstImageMatchingHref(href)
                    self.cache['images'].append({
                        'href': href,
                        'title': firstMatch['title'],
                        'alt': firstMatch['alt'],
                    })
        return self.cache['images']

    @property
    def creator(self):
        """ Sets the creator of the epub
        """
        if not 'creator' in self.cache:
            elem = self.rootFile.find('metadata').find('creator')
            if elem != None:
                self.cache['creator'] = elem.text
            else:
                self.cache['creator'] = None
        return self.cache['creator']

    @property
    def language(self):
        """ Checks for the language of the book found in the metadata
        """
        elem = self.rootFile.find('metadata').find('language')
        if elem != None:
            return elem.text
        return None

    @property
    def ploneID(self):
        """ Returns a title that can be turned into an id with the use of
        titleToId
        """
        return titleToId(self.title)

class ImportView(BrowserView):
    """ ImportView Browserview
    """
    def __call__(self):
        if self.request.environ['REQUEST_METHOD'] == 'POST':
            httpFileUpload = self.request.form.values()[0]
            try:
                self.importFile(httpFileUpload) # new-id =
            except Exception, err:
                logger.debug(err)
                return self.request.response.redirect(
                    self.context.absolute_url() +
                    "/edit?portal_status_message=An error occur during upload,"
                    "your EPUB format may not be supported")
            return self.request.response.redirect(self.context.absolute_url())

    def importFile(self, epubFile):
        """ Imports the epub file
        """
        zipFile = ZipFile(epubFile, 'r')
        epub = EpubFile(zipFile)

        transaction.savepoint()

        context = self.context
        context.setTitle(epub.title)
        if epub.creator != None:
            context.setCreators([epub.creator])

        annotations = IAnnotations(context)
        mapping = annotations['eea.epub'] = PersistentDict({'toc': []})
        mapping['toc'] = epub.tocNavPoints

        alsoProvides(context, IImportedBook)
        context.reindexObject()

        # Save original file, we might need it later
        original = context[context.invokeFactory('File', id='original.epub')]
        original.setFile(epubFile)
        field = original.getField('file')
        field.getRaw(original).setContentType('application/epub+zip')

        if epub.coverImageData != None:
            context.invokeFactory('Image', id='epub_cover',
                                  image=epub.coverImageData)

        for image in epub.images:
            workingDirectory = context
            urlParts = image['href'].split('/')
            for urlPart in urlParts:
                if urlPart == urlParts[-1]:
                    path = 'OEBPS/' + image['href']
                    path = urllib.unquote(path)
                    data = epub.zipFile.read(path)
                    urlPart = cleanNames(urlPart)
                    obj = workingDirectory[workingDirectory.invokeFactory(
                            'Image', id=urlPart, image=data)]
                    obj.setTitle(image['title'])
                    obj.setDescription(image['alt'])
                    alsoProvides(obj, IImportedImage)
                    obj.reindexObject()
                elif not urlPart in workingDirectory.objectIds():
                    workingDirectory = \
                    workingDirectory[workingDirectory.invokeFactory('Folder',
                                                                    id=urlPart)]
                else:
                    workingDirectory = workingDirectory[urlPart]

        for resource in epub.page_resources:
            article = context[context.invokeFactory('Document',
                                                    id=resource['id'])]
            article.setTitle(resource['title'])
            article.setText(resource['content'])
            article.setDescription(resource['description'])
            article._at_rename_after_creation = False
            if resource['isChapter']:
                alsoProvides(article, IImportedChapter)
            article.reindexObject()

        newId = context._renameAfterCreation(check_auto_id=False)
        return newId
