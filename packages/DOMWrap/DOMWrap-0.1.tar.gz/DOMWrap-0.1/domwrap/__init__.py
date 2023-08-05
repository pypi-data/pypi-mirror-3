from xml.dom import minidom
from xml import dom


def parseString(*args, **kwargs):
	'''Alias for minidom.parseString. Wraps result in a DocumentWrapper object.'''
	return DocumentWrapper(minidom.parseString(*args, **kwargs))


def parse(*args, **kwargs):
	'''Alias for minidom.parse. Wraps result in a DocumentWrapper object.'''
	return DocumentWrapper(minidom.parse(*args, **kwargs))


class DocumentWrapper(object):
	'''Wrapper for minidom.Document.'''
	def __init__(self, doc):
		self.doc = doc
		
	def __getitem__(self, index):
		return ElementList([self.doc])[index]
		
		
class NodeWrapper(object):
	'''Wrapper for minidom.Element.'''
	
	def __init__(self, node):
		self.node = node
		
	def __getitem__(self, index):
		if index.startswith("@"):
			return ElementList([self.node])[index][0]
		else:
			return ElementList([self.node])[index]
		
	@property
	def text(self):
		'''Returns joined list of all text nodes.'''
		return "".join(ElementList([self.node]).textNodes)

	@property
	def textNodes(self):
		'''Returns a list of all text nodes that are children of self.node.'''
		return ElementList([self.node]).textNodes
		
	@property
	def name(self):
		'''Alias for self.node.nodeName.'''
		return self.node.nodeName
		
	def __repr__(self):
		return "<NodeWrapper %s>" % self.node.nodeName
		
	
class ElementList(object):
	def __init__(self, children):
		self.children = children
		
	def __eq__(self, other):
		return self.children == other.children
		
	def __iter__(self):
		for x in self.children:
			yield NodeWrapper(x)
		
	def iterList(self, list):
		'''Filters out all nodes that can't have child nodes.'''
		for x in list:
			if x.nodeType == dom.Node.ELEMENT_NODE or x.nodeType == dom.Node.DOCUMENT_NODE:
				yield x
		
	def __getitem__(self, other):
		'''XPath-like syntax for querying children. Use 'foo' to fetch all child elements named foo. Use '/foo' to fetch from all descendants. Use '@foo' to fetch attributes.'''
		
		if isinstance(other, slice):
			return ElementList(self.children.__getitem__(other))
		
		l = []
		
		if isinstance(other, int):
			return NodeWrapper(self.children[other])
		
		if other.startswith("@"):
			return self.getAttribute(other[1:])
		elif other.startswith("/"):
			return self.getAllSubElements(other[1:])
			
		for element in self.children:
			for child in self.iterList(element.childNodes):
				if child.tagName == other:
					l.append(child)
				
		return ElementList(l)
			
	def getAttribute(self, name):
		l = []
		for element in self.children:
			if element.hasAttribute(name):
				l.append(element.getAttribute(name))
				
		return l
		
	def getAllSubElements(self, name):
		'''For every child calls getElementsByTagName and wraps result in ElementList'''
		l = []
		for x in self.iterList(self.children):
			for element in x.getElementsByTagName(name):
				l.append(element)
				
		return ElementList(l)
		
		
	@property
	def textNodes(self):
		l = []
		
		for x in self.children:
			for child in x.childNodes:
				if child.nodeType == dom.Node.TEXT_NODE or child.nodeType == dom.Node.CDATA_SECTION_NODE:
					l.append(child.nodeValue)
					
		return l
					
		
	def __repr__(self):
		return "<ElementList %s>" % self.children
				
				
				
if __name__ == "__main__":
	import unittest
	
	class Test(unittest.TestCase):
		def test_queries(self):
			doc = minidom.parseString("<a attribute='doc'><b><c>c content</c>b content</b><d test='1'>d content</d><d>d content 2</d></a>")
			doc = DocumentWrapper(doc)
	
			self.assertEquals(doc["a"]['b']["c"][0].text, 'c content')
			self.assertEquals(doc['a'][0]['@attribute'], "doc")
			self.assertEquals(doc['/d'].textNodes, ['d content','d content 2'])

			self.assertEquals(len(list(doc['a'])), 1)
			self.assertEquals(list(doc['a']['b']['c'])[0].text, "c content")

			self.assertEquals(doc['/d'][0].text, "d content")
			self.assertEquals(doc['/d'][1].text, "d content 2")

			self.assertEquals(doc['/d'][0:2].textNodes, ['d content','d content 2'])

			self.assertEquals(doc['/d'][0].name, "d")
			
			self.assertEquals(doc['/b'][0]['c'], ElementList([doc["/b"][0].node])["c"])
			
			
	unittest.main()
