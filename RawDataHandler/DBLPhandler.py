import xml.sax


class authorHandler(xml.sax.ContentHandler):  # extract all authors
    def __init__(self):
        self.CurrentData = ""  # tag's name
        self.dict = {}  # save all authors. The key is an author's name, the value is his id
        self.name = ""  # the name of an author
        self.id = 0  # the ID of an author

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        self.name = ""

    def endElement(self, tag):
        if self.CurrentData == 'author':  # this tag is author, save it in the dict
            exist = self.dict.get(self.name, -1)
            if exist == -1:  # if this author have not been added into dict
                self.dict[self.name] = self.id
                self.id = self.id + 1
                self.name = ""

    def characters(self, content):
        if self.CurrentData == 'author':
            self.name += content


class collabrationHandler(xml.sax.ContentHandler):  # extract all collaboration relations
    def __init__(self, dict, file):
        self.CurrentData = ""  # tag's name
        self.dict = dict  # the author-ID dict
        self.name = ""  # the name of an author
        self.id = 0  # the ID of an author
        self.paper = False  # if the tag is article or inproceeding, paper = True
        self.author = []  # all authors' id in one <article> or <inproceeding>
        self.file = file  # Output collaboration relation to file
        self.edge = set()  # Edge's set
        self.time_year = None

    def startElement(self, tag, attributes):
        self.CurrentData = tag

        if tag == 'article' or tag == 'inproceeding':
            self.author.clear()  # start processing a new paper, old collaboration neen to be deleted
            self.paper = True

    def endElement(self, tag):
        if (tag == 'article' or tag == 'inproceeding') and self.paper is True:  # One paper's tag close
            self.paper = False
            t = self.time_year
            for i in self.author:
                for j in self.author:
                    if i < j :  # edge
                        self.file.write(str(i) + ',' + str(j)+ ';'+t + '\n')
                        self.edge.add((i, j))

    def characters(self, content):

        if self.paper:
            self.name = content
            isAuthor = self.dict.get(self.name, -1)  # isAuthor == -1 means that this content is not an author's name
            if isAuthor != -1:
                self.author.append(self.dict[self.name])  # add this author's id
        if self.CurrentData == "year":
            if len(content) == 4:
                self.time_year = content
                # print(self.time_year)


# set xml parser
parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
handler1 = authorHandler()
parser.setContentHandler(handler1)
parser.parse('/Users/cherudim/Desktop/dblp.xml')
#
with open('author.txt', 'w') as f:
    for k, v in handler1.dict.items():
        f.write(str(v))
        f.write(' ' + k)
        f.write('\n')
f.close()

with open('collaboration.txt', 'w') as f:
    handler2 = collabrationHandler(handler1.dict, f)
    parser.setContentHandler(handler2)
    parser.parse('/Users/cherudim/Desktop/dblp.xml')
f.close()
