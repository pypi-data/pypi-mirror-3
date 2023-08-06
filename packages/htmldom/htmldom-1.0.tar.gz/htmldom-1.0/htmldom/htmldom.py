"""
HTMLDOM Library provides a simple interface for accessing and manipulating HTML documents.
You may find this library useful for building applications like screen-sraping.
Inspired by Jquery Libray.
"""
import re

elementName = r'<([\w_]+)'
restName = r'(?:\s+)?((?:[\w_:-]+\s*\=\s*[\'"](?:[^"]+)?[\'"]\s*;?)*)?\s*(?:/)?>'

#StartTag
startTag = re.compile(elementName + restName)

#endTag
endTag = re.compile(r'\s*</\s*([\w_]+)\s*>')


whiteSpace = re.compile(r'\s+')

#Used to spilt attributes into name/value pair i.e. ( class="one" ==> { 'class':'one' } )
attributeSplitter = re.compile(r'(?:([\w_:-]+)\s*\=\s*[\'"]([^"]+)[\'"]\s*)')

#These regex are used for class and id based selection.
"""
  i.e. given p.class#id
  @regVar:selector matches the "p" element and @regVar:left will contain ".class"
  and @regVar:right will hold the "#id" part.
"""
selector = re.compile(r'([\w_:-]+)?((?:[#.\[][%?&+\s\w_ /:.\d#(),;\]\'"=$^*-\\]+)*)?')

sep = r'(?:(?:[.#](?:[\w_:./-]+))'
leftSelector = r'|(?:\[\s*[\w_:-]+\s*(?:[$*^]?\s*\=\s*[\'"]\s*[^"]+\s*[\'"])?\s*\]))?'
left = '('+sep + leftSelector+')'
right = r'((?:[%#.\[][^"]+)*)?'

newSelector = re.compile('(?:'+left + right+')?')

#This regex is used to detect [href*=someVal] | [href^=some_val] | [href$='someVal']
attributeSubStringSelector = re.compile(r'([*$^])\s*\=')

stripChars = "^M"

class HtmlDomNode:
	def __init__( self, nodeName="text",nodeType=3):
		self.nodeName = nodeName
		self.nodeType = nodeType
		self.parentNode = None
		self.nextSiblingNode = None
		self.previousSiblingNode = None
		self.children = []
		self.attributes = {}
		self.ancestorList = []
		self.text = ""
	def setParentNode( self, parentNode ):
		self.parentNode = parentNode
		return self
	def setSiblingNode( self, siblingNode ):
		self.nextSiblingNode = siblingNode
		return self
	def setPreviousSiblingNode( self, siblingNode ):
		self.previousSiblingNode = siblingNode
		return self
	def setChild( self, child ):
		self.children.append( child )
		return self
	def setAttributes( self, attributeDict ):
		self.attributes.update( attributeDict )
		return self
	def setAncestor( self, nodeList ):
		self.ancestorList = list(nodeList)
		return self
	def setText( self, text ):
		self.text = text
		return self
	def setAsFirstChild(self,node ):
		self.children.insert(0,node)
		return self

	def setAncestorsForChildren( self, ancestor ):
		for childNode in self.children:
			childNode.setAncestor( childNode.ancestorList + ancestor )
			childNode.setAncestorsForChildren( ancestor )
		return self

	def firstChild(self):
		return self.children[0]
	def lastChild(self):
		return self.children[-1]
	def getPreviousSiblingNode(self):
		return self.previousSiblingNode
	def getAncestorList(self):
		return self.ancestorList
	def getName(self):
		return self.nodeName
	def html(self):
		htmlStr = ""
#		if self.nodeType == 1:
		htmlStr += "<" + self.nodeName + " "
		for attrName in self.attributes:
			htmlStr += attrName +"="+'"'+" ".join(self.attributes[attrName]) + '" '
		htmlStr += '>'
		for node in self.children:
			if node.nodeType == 3:
				htmlStr += node.text
			else:
				htmlStr += node.html()
		htmlStr += '</'+self.nodeName +'>\n'
		return htmlStr

	def getText(self):
		textStr = ""
		for node in self.children:
			if node.nodeType == 3:
				textStr += node.text
			else:
				textStr += node.getText() + '\n'
		return textStr
	def getNextSiblings(self):
		siblingsSet = []
		node = self.nextSiblingNode
		while node:
			if node not in siblingsSet:
				siblingsSet.append(node)
			node = node.nextSiblingNode
		return siblingsSet
	def getPreviousSiblings(self):
		siblingsSet = []
		node = self.previousSiblingNode
		while node:
			if node not in siblingsSet:
				siblingsSet.append(node)
			node = node.previousSiblingNode
		return siblingsSet


class HtmlDom:
	def __init__( self, url ):
		self.baseURL = url

		#@var:domNodes is a dictionary which holds all the tags present in the page.
		# So that it will be very easy to look up the tags when queried.
		self.domNodes = {}
		self.domNodesList = []
		self.referenceToRootElement = None

	def createDom(self,htmlString=None):
		if htmlString:
			data = htmlString
		else:
			try:
				try:
					import urllib2
				except ImportError:
					#For python3
					import urllib.request as urllib2
				request = urllib2.Request(self.baseURL)
				request.add_header('User-agent','Mozilla/9.876 (X11; U; Linux 2.2.12-20 i686, en; rv:2.0) Gecko/25250101 Netscape/5.432b1 (C-MindSpring)')
				response = urllib2.urlopen(request)
				data = response.read().decode('utf-8')
				self.parseHTML( data )
				self.domDictToList()
			except Exception:
				print("Error while reading url: %s" % (self.baseURL))

		return self
	def parseHTML( self, data ):
		index = 0

		#Node stack will hold the parent Nodes. The top most node will be the current parent.
		nodeStack = []

		while data:
			data = data.strip().rstrip()
			#Doctype tag
			if data.find("<!DOCTYPE") == 0 or data.find("<!doctype") == 0:
				#Just pass through the doctype tag.
				index = data.find(">")
				data = data[ index + 1:].strip()
				continue
			#Comment Node
			if data.find("<!--") == 0:
				#Just pass through the comment node.
				index = data.find("-->")
				data = data[index + len("-->"):].strip()
				continue

			#index is just used for extracting texts withing the tags.
			#could change in future.
			index = data.find("<")

			# len(nodeStack) >= 1 means found text content between the end of a tag and the start of a new tag
			if len( nodeStack ) >= 1:
				_index = -1
				#if script element is on the top of the stack then entire content of it will be stored in a single text node
				if nodeStack[-1].getName() == "script":
					_index = data.find("</script>")
					if _index != -1:
						tmpData = data[:_index]
				elif nodeStack[-1].getName() == "style":
					_index = data.find("</style>")
					if _index != -1:
						tmpData = data[:_index]
				else:
					tmpData = data[:index]
				#tmpData should not be empty.
				if tmpData:
					textNode = HtmlDomNode("text")
					textNode.setText(tmpData)
					if len(nodeStack) > 0:
						textNode.setParentNode(nodeStack[-1])
						nodeStack[-1].setChild(textNode)
					if _index != -1:
						data = data[_index:].strip()
					else:
						data = data[index:].strip()
				else:
					data = data.strip()
			#end of a tag
			if data.find("</") == 0:
				match = endTag.search( data )
				data = data[len(match.group()):].strip(' ').rstrip('')
				try:
					nodeStack.pop()
					continue
				except IndexError:
					nodeStack = []

			#start of a tag.
			if data.find("<") == 0:
				match = startTag.search( data )
				if not match:
					#Fail silently
					continue
				#match.group(1) will contain the element name
				elementName = match.group(1)
				domNode = HtmlDomNode( elementName,1)
				attr = match.group(2)
				if attr:
					#converting multispaces into single space.for easy handling of attributes
					attr = whiteSpace.sub( ' ', attr.strip() )
					attr = attributeSplitter.findall( attr )
					attrDict = {}
					for attrName,attrValues in attr:
						attrDict[attrName] = attrValues.split()
					domNode.setAttributes( attrDict )
				if len(nodeStack) > 0:
					#set the sibling node.
					if len(nodeStack[-1].children) > 0:
						nodeStack[-1].children[-1].setSiblingNode( domNode )
						domNode.setPreviousSiblingNode( nodeStack[-1].children[-1] )

					# nodeStack[-1] gives the current parent node present on the top of the stack.
					nodeStack[-1].setChild(domNode)
					domNode.setParentNode( nodeStack[-1] )

					#setting ancestor list
					domNode.setAncestor( nodeStack[::-1] )

					#push the current node into the stack.so now domNode becomes the current parent node.
					#if the current node is an empty element,do not push the element into the stack.
					if match.group().find("/>") == -1:
						nodeStack.append( domNode )
				else:
					domNode.setAncestor( nodeStack )
					nodeStack.append( domNode )
					self.referenceToRootElement = domNode

				self.registerNode( domNode.nodeName, domNode )
				#print(match.group(),end='')
				#input()
				data = data[len(match.group()):].strip()
			else:
				data = data[1:]

	def registerNode( self, nodeName, domNode ):
		if self.domNodes.get(nodeName,None):
			self.domNodes[nodeName] += [domNode]
		else:
			self.domNodes[nodeName] = [domNode]
	def updateDomNodes( self, newDomNodes ):
		for nodeName in newDomNodes:
			self.domNodes[nodeName] += newDomNodes[nodeName]
	def getDomDict(self):
		return self.domNodes

	def domDictToList(self):
		for nodeName in self.domNodes:
			for selectedNode in self.domNodes[nodeName]:
				#Converting the dictionary into a list of values.
				self.domNodesList.append( selectedNode )
	def find(self,selectors):
		classSelector = []
		idSelector = []
		attributeSelector = {}
		attributeSelectorFlags = {
		                           '$':False,'^':False,'*':False,'noVal':False
		                         }
		selectorMethod = {'+':False,'>':False}
		nodeList = []
		selectors = re.sub(r'([+>])',r' \1 ',selectors)
		selectors = whiteSpace.sub( ' ', selectors )
		selectors = selectors.split()
		data = ""
		elemName = ""
		for value in selectors:
			if value == '+' or value == '>':
				selectorMethod[value] = True
				continue
			if value == '*':
				return HtmlNodeList( self.domNodesList, self )
			match = selector.search( value )
			if match:
				elemName = match.group(1)
				data = match.group(2)
				while data:
					match = newSelector.search( data )
					if match:
						data = match.group(2)
						#class selector
						if match.group(1).find(".") == 0:
							index = match.group(1).find(".")
							classSelector.append( match.group(1)[index+1:] )
						elif match.group(1).find("#") == 0:
							index = match.group(1).find("#")
							idSelector.append( match.group(1)[index +1:] )
						elif match.group(1).find("[") == 0:
							index = match.group(1).find("]")
							attr = match.group(1)[1:][:-1]
							attrMatch = re.search( attributeSubStringSelector, attr )
							if attrMatch:
								attributeSelectorFlags[attrMatch.group(1)] = True
								_index = attr.find(attrMatch.group(1))
								attr = attr[:_index - len(attr)] + attr[_index + 1:]
								attr = attr.split("=")
							elif attr.find("=") == -1:
								#Only attribute name is given not the value.
								attributeSelectorFlags['noVal'] = True
								attr = attr.split()
								attr.append('')
							else:
								attr = attr.split("=")
							attr[1] = re.sub(r'\'','',attr[1])
							attributeSelector[attr[0]] = attr[1]
				if elemName:
					nodes = self.domNodes.get( elemName, [] )
				else:
					if classSelector:
						nodes = self.getNodesWithClassOrId(classSelector[-1],selectType='class')
					elif idSelector:
						nodes = self.getNodesWithClassOrId(idSelector[-1],selectType='id')
					elif attributeSelector:
						#new Addition:Mon 13 Feb
						nodes = self.getNodesWithAttributes(attributeSelector,attributeSelectorFlags)
				tmpList = []
				for node in nodeList:
					if selectorMethod['+']:
#						[ tmpList +=self.getUniqueNodes(tmpList,[selectedNode]) for selectedNode in nodes if node.nextSiblingNode == selectedNode ]
						for selectedNode in nodes:
							if node.nextSiblingNode == selectedNode:
								tmpList +=self.getUniqueNodes(tmpList,[selectedNode])
						selectorMethod['+'] = False
					elif selectorMethod['>']:
#						[ tmpList +=self.getUniqueNodes(tmpList,[selectedNode]) for selectedNode in nodes if selectedNode in node.children ]
						for selectedNode in nodes:
							if selectedNode in node.children:
								tmpList +=self.getUniqueNodes(tmpList,[selectedNode])
						selectorMethod['>'] = False
					else:
#						[ tmpList +=self.getUniqueNodes(tmpList,[selectedNode]) for selectedNode in nodes if node in selectedNode.ancestorList ]
						for selectedNode in nodes:
							if node in selectedNode.ancestorList:
								tmpList +=self.getUniqueNodes(tmpList,[selectedNode])
				if not nodeList:
					tmpList = nodes
				nodes = tmpList
				nodeList = []
				for node in nodes:
					nodeAccepted = True
					for value in classSelector:
						if value not in node.attributes.get('class',[]):
							nodeAccepted = False
							break
					if nodeAccepted:
						for value in idSelector:
							if value not in node.attributes.get('id',[]):
								nodeAccepted = False
								break
					if nodeAccepted:
						if attributeSelector:
							nodeAccepted = self.getNodesWithAttributes(attributeSelector,attributeSelectorFlags,[node])
					if nodeAccepted:
						nodeList.append(node)
				classSelector = []
				idSelector = []
				attributeSelector = {}
				attributeSelectorFlags = {'$':False,'^':False,'*':False,'noVal':False}
			if not nodeList:
				break
		return HtmlNodeList( nodeList,self )
	def getNodesWithClassOrId( self,className="",nodeList = None,selectType=""):
		tmpList = []
		for nodeName in self.domNodes:
			[ tmpList.append( selectedNode ) for selectedNode in self.domNodes[nodeName] if className in selectedNode.attributes.get(selectType,['']) ]
		return tmpList
	def getNodesWithAttributes( self, attributeSelector,attributeSelectorFlags,nodeList = None):
		tmpList = self.domNodesList
		"""
		for nodeName in self.domNodes:
			for selectedNode in self.domNodes[nodeName]:
				#Converting the dictionary into a list of values.
				tmpList.append( selectedNode )
		"""
		if nodeList:
			tmpList = nodeList
		key,attrValue = list(attributeSelector.items())[0]
		newList = []
		for node in tmpList:
			nodeAccepted = True
			if attributeSelectorFlags['$']:
				if attributeSelector[key] not in node.attributes.get(key,[''])[-1][len(node.attributes.get(key,[''])[-1])::-1]:
					nodeAccepted = False
			elif attributeSelectorFlags['^']:
				if attributeSelector[key] not in node.attributes.get(key,[''])[0]:
					nodeAccepted = False
			elif attributeSelectorFlags['*']:
				if attributeSelector[key] not in " ".join(node.attributes.get(key,[])):
					nodeAccepted = False
			elif attributeSelectorFlags['noVal']:
				if key not in node.attributes:
					nodeAccepted = False
			elif attributeSelector[key] != " ".join(node.attributes.get(key,[])):
				nodeAccepted = False
			if nodeAccepted:
				newList.append(node)
		return newList
	def getUniqueNodes(self,srcList, newList ):
		tmpList = []
		for selectedNode in newList:
			if selectedNode not in srcList:
				tmpList.append( selectedNode  )
		return tmpList

class HtmlNodeList:
	def __init__( self, nodeList,dom,prevNodeList=[],prevObject = None):
		self.nodeList = nodeList
		self.htmlDom = dom
		self.previousNodeList = prevNodeList
		if not prevObject:
			self.referenceToPreviousNodeListObject = self
		else:
			self.referenceToPreviousNodeListObject = prevObject
	def children(self):
		childrenList = []
		for node in self.nodeList:
			[ childrenList.append(child) for child in node.children if child.nodeType == 1]
		return HtmlNodeList( childrenList,self.htmlDom,self.nodeList,self)
	def html(self):
		htmlStr = ""
		for node in self.nodeList:
			htmlStr += node.html()
		return htmlStr
	def text(self):
		textStr = ""
		for node in self.nodeList:
			textStr += node.getText()
		return textStr
	def attr( self, attrname ):
		if len( self.nodeList ) > 0:
			return self.nodeList[0].attributes.get( attrName,"Undefined attribute" )
		else:
			raise Exception("Index out of range")
			
	def filter(self,selector):
		nList = self.htmlDom.find(selector)
		tmpList = []
		for node in self.nodeList:
			if node in nList.nodeList:
				tmpList += self.getUniqueNodes( tmpList, [node] )
		return HtmlNodeList( tmpList,self.htmlDom, self.nodeList,self)
	def _not(self,selector ):
		nList = self.htmlDom.find(selector)
		tmpList = []
		for node in self.nodeList:
			if node not in nList.nodeList:
				tmpList.append( node )
		return HtmlNodeList( tmpList,self.htmlDom, self.nodeList, self)
	def eq(self,index ):
		if index > -len(self.nodeList) and index < len( self.nodeList ):
			return HtmlNodeList([self.nodeList[index]],self.htmlDom, self.nodeList,self)
		else:
			print("Index Out Of Range.")
	def first( self ):
		return self.eq(0)
	def last( self ):
		return self.eq( len(self.nodeList ) - 1 )
	def has(self,selector ):
		nList = self.htmlDom.find(selector)
		tmpList = []
		for node in self.nodeList:
			[ tmpList.append( node ) for selectedNode in nList.nodeList if node in selectedNode.ancestorList ]
		return HtmlNodeList( tmpList,self.htmlDom, self.nodeList,self)
	def _is(self,selector):
		val = self.filter(selector)
		if val.nodeList:
			return True
		else:
			return False
	def next(self):
		tmpList = []
		for node in self.nodeList:
			if node.nextSiblingNode:
				tmpList.append(node.nextSiblingNode)
		return HtmlNodeList( tmpList, self.htmlDom, self.nodeList,self)
	def nextAll(self):
		tmpList = []
		for node in self.nodeList:
			tmpList += node.getNextSiblings()
		return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self)

	def nextUntil(self,selector):
		nList = self.htmlDom.find(selector)
		siblingsSet = []
		tmpList = []
		selectedNodeList = []
		for node in self.nodeList:
			#This function gets all the siblings.
			tmpList = node.getNextSiblings()
			for selectedNode in nList.nodeList:
				try:
					index = tmpList.index( selectedNode )
					selectedNodeList = tmpList[:index]
					siblingsSet += self.getUniqueNodes( siblingsSet, selectedNodeList )
					break
				except ValueError:
					pass
			else:
				siblingsSet += self.getUniqueNodes( siblingsSet, tmpList )
		return HtmlNodeList( siblingsSet,self.htmlDom, self.nodeList, self)
	def prev(self):
		tmpList = []
		for node in self.nodeList:
			if node.previousSiblingNode:
				tmpList.append(node.previousSiblingNode)
		return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self)
	def prevAll(self):
		tmpList = []
		for node in self.nodeList:
			tmpList += node.getPreviousSiblings()
		return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self)
	def prevUntil(self,selector):
		nList = self.htmlDom.find(selector)
		siblingsSet = []
		tmpList = []
		selectedNodeList = []
		for node in self.nodeList:
			#This function gets all the previous siblings.
			tmpList = node.getPreviousSiblings()
			for selectedNode in nList.nodeList:
				try:
					index = tmpList.index( selectedNode )
					selectedNodeList = tmpList[:index]
					siblingsSet += self.getUniqueNodes( siblingsSet, selectedNodeList )
					break
				except ValueError:
					pass
			else:
				siblingsSet += self.getUniqueNodes( siblingsSet, tmpList )
		return HtmlNodeList( siblingsSet,self.htmlDom, self.nodeList, self)
	def siblings(self,selector=""):
		prevSiblingsSet = []
		nextSiblingsSet = []
		siblingsSet = []
		for node in self.nodeList:
			prevSiblingsSet = node.getPreviousSiblings()
			siblingsSet += self.getUniqueNodes( siblingsSet, prevSiblingsSet )
			nextSiblingsSet = node.getNextSiblings()
			siblingsSet += self.getUniqueNodes( siblingsSet, nextSiblingsSet )
		return HtmlNodeList( siblingsSet, self.htmlDom, self.nodeList,self )
	def parent(self):
		tmpList = []
		for node in self.nodeList:
			if node.parentNode:
				tmpList.append(node.parentNode)
		return HtmlNodeList( tmpList, self.htmlDom, self.nodeList,self)
	def parents(self):
		tmpList = []
		for node in self.nodeList:
			tmpList += node.ancestorList
		return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self)
	def parentsUntil(self,selector):
		nList = self.htmlDom.find(selector)
		parentsList = []
		tmpList = []
		selectedNodesList = []
		for node in self.nodeList:
			tmpList = node.ancestorList
			for selectedNode in nList.nodeList:
				try:
					index = tmpList.index( selectedNode )
					selectedNodeList = tmpList[:index]
					parentsList += self.getUniqueNodes( parentsList, selectedNodeList )
					break
				except ValueError:
					pass
			else:
				parentsList += self.getUniqueNodes( parentsList, tmpList )
		return HtmlNodeList( parentsList, self.htmlDom, self.nodeList, self)
	def add(self,selector):
		nList = self.htmlDom.find(selector)
		newNodeList = self.nodeList + self.getUniqueNodes( self.nodeList, nList.nodeList )
		return HtmlNodeList( newNodeList, self.htmlDom, self.nodeList,self )

	#This functions will be implemented in the next version.
	"""
	def append( self, data ):
		if isinstance( data, str ):
			#If it is a html data
			#Since html tags begings with "<"
			if data.lstrip().find("<") == 0:
				for node in self.nodeList:
					newDom = HtmlDom().createDom(data)
					root = newDom.referenceToRootElement
					self.htmlDom.updateDomNodes( newDom.getDomDict() )
					root.setParentNode( node ).setPreviousSiblingNode( node.lastChild() )
					node.lastChild().setSiblingNode( root )
					node.setChild( root )
					ancestor = [node] + node.getAncestorList()
					root.setAncestor( ancestor )
					root.setAncestorsForChildren( ancestor )
			else:
				#data is a plain string.
				#construct a text node and append it to the current node
				for node in self.nodeList:
					newTextNode = HtmlDomNode().setText(data)
					newTextNode.setParentNode(node)
					node.setChild(newTextNode)
		return self
	def prepend( self, data ):
		if isinstance( data, str ):
			#If it is a html data
			#Since html tags begings with "<"
			if data.lstrip().find("<") == 0:
				for node in self.nodeList:
					newDom = HtmlDom().createDom(data)
					root = newDom.referenceToRootElement
					self.htmlDom.updateDomNodes( newDom.getDomDict() )
					root.setParentNode( node ).setSiblingNode( node.firstChild() )
					node.firstChild().setPreviousSiblingNode( root )
					node.setAsFirstChild( root )
					ancestor = [node] + node.getAncestorList()
					root.setAncestor(  ancestor )
					root.setAncestorsForChildren( ancestor )
			else:
				#data is a plain string.
				#construct a text node and append it to the current node
				for node in self.nodeList:
					newTextNode = HtmlDomNode().setText(data)
					node.setAsFirstChild(newTextNode)
		return self
	"""
	def andSelf(self):
		newList = []
		newList += self.getUniqueNodes( newList, self.previousNodeList )
		newList += self.getUniqueNodes( newList, self.nodeList )
		return HtmlNodeList( newList, self.htmlDom, self.nodeList,self )
	def end(self):
		return HtmlNodeList( self.previousNodeList, self.htmlDom, self.referenceToPreviousNodeListObject.referenceToPreviousNodeListObject.nodeList,self.referenceToPreviousNodeListObject.referenceToPreviousNodeListObject )

	def write( self,fileName ):
		import codecs
		fp = codecs.open( fileName, "w","utf-8")
		#fp = open( fileName ,"w")
		fp.write( self.html() )
		fp.close()
		return self
	def length(self):
		return len(self.nodeList)
	def contains( self, pattern ):
		pattern = re.compile( pattern )
		selectedNodeList = []
		for node in self.nodeList:
		  text = node.getText()
		  if pattern.search( text ):
		    selectedNodeList += self.getUniqueNodes( selectedNodeList, [node] )
		return HtmlNodeList( selectedNodeList, self.htmlDom, self.nodeList, self )
	def toList(self):
	    return self.nodeList

	def getUniqueNodes(self,srcList, newList ):
		tmpList = []
		for selectedNode in newList:
			if selectedNode not in srcList:
				tmpList.append( selectedNode  )
		return tmpList
