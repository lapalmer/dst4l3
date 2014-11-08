#!/usr/bin/env python

import urllib,string,re,sys,os

RETRIEVEURL='''&lt;a href=&quot;http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?db=pubmed&amp;cmd=Retrieve&amp;list_uids=%s&amp;dopt=Abstract&quot;&gt;Link to Article in PubMed&lt;/a&gt;'''

SEARCHURL='''http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=medline&retmode=text&email=mary.piorun@umassmed.edu'''

HEAD='''<?xml version="1.0" encoding="UTF-8"?> 
<documents xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.bepress.com/document-import.xsd">
'''

DOCUBLOCK='''
<document>
<title>%s</title>
<publication-date>%s</publication-date>
<authors>
%s
</authors>
<subject-areas>
%s</subject-areas>
%s
%s
</document>
'''
AUTHBLOCK='''
<author xsi:type="individual">
  <email>%s</email> 
  <institution>%s</institution> 
  <lname>%s</lname> 
  <fname>%s</fname> 
  </author>
'''
SUBJSTR='<subject-area>%s</subject-area>\n'
ABSTSTR='<abstract>%s</abstract>'

ARTINFO='''
<fulltext-url>DOCUMENTBASE/%s.pdf</fulltext-url>
<document-type>article</document-type>
<fields>
%s
</fields>
''' 

FIELDSTR='''<field name="%s" type="string">
<value>%s</value></field>'''

DOISTR='''&lt;a href=&quot;http://dx.doi.org/%s&quot;&gt;Link to article on publisher&apos;s site&lt;/a&gt;'''

FOOTER='</documents>'

class Ref:
    "A class to manage Medline Objects"
    
    def __init__(self):
        self.pmid=""
        self.issn=""
        self.pubdate=""
        self.vol=""
        self.inum=""
        self.journal=""
        self.address=""
        self.citation=""
        self.authors=[]
        self.title=""
        self.abstract=""
        self.subjects=[]
        self.sMESH=""
        self.sAuthors=""
        self.doi=""
        self.pages=""
        
    def setPmid(self,id):
        self.pmid=id
    def getPmid(self):
        return self.pmid
        
    def setAddress(self,addr):
        if self.address !="":
            self.address += " " + addr
        else:
            self.address=addr
    def getAddress(self):
        adflds=string.split(self.address,',')
        return adflds[0]
        
    def setISSN(self,issn):
        self.issn=issn
        
    def getISSN(self):
        if self.issn != "":
            return self.issn
        return ""
        
    def setPubdate(self,pubdate):
        dts=string.split(pubdate,' ')
        self.pubdate=re.sub('/','-',dts[0])
        
    def getPubdate(self):
        if self.pubdate !="":
            return self.pubdate
        return ""
        
    def setVol(self,vol):
        self.vol=vol
    
    def getVol(self):
        if self.vol !="":
            return self.vol
        return ""

    def setInum(self,inum):
        self.inum=inum
        
    def getInum(self):
        if self.inum != "":
            return self.inum
        return ""
        
    def setJournal(self,journal):
        if self.journal != "":
            self.journal += " "+journal
        else:
            self.journal=journal
    
    def getJournal(self):
        if self.journal != "":
            return self.journal
        return ""
        
    def setPages(self,pages):
        self.pages=pages
        
    def getPages(self):
        if self.pages !="":
            return self.pages
        return ""
        
    def setCitation(self,citation):
        self.citation=citation
        
    def getCitation(self):
        if self.citation != "":
            return "Citation: %s %s" % (self.citation,self.getDOI())
        return ""
        
    def setAuthors(self,author):
        self.authors.append(author)
        
    def getLastauthor(self):
        if len(self.authors) != 0 :
            return self.authors[len(self.authors)-1]
        else:
            return ""
            
    def setShortAuth(self,author):
        pAuth=self.getLastauthor()
        if pAuth:
            Names=string.split(pAuth,',',2)
            if author == Names[0]+" "+Names[1][:1]: return
        else:
            Names=string.split(author,' ',2)
            self.authors.append(Names[0]+', '+Names[1])
            
    def getAuthors(self,authblock):
        self.sAuthors=""
        for author in self.authors:
            lastname,firstname=string.split(author,', ',2)
            self.sAuthors+=authblock % ("","",lastname,firstname)
        
    def setTitle(self,title):
        if self.title != "":
            self.title+= " "+ title
        else:
            self.title=title
            
    def getTitle(self):
        if self.title !="":
            return self.zapPunct(self.title)
        return ""

            
    def setAbstract(self,abstract):
        if self.abstract != "":
            self.abstract += " "+abstract
        else:
            self.abstract=abstract
            
    def getAbstract(self,ABST):
        if self.abstract != "": return ABST % re.sub('<','&lt;',self.abstract)
        return " "
            
    def setMESH(self,mesh):
        mheads=string.split(mesh,'/',2)
        self.subjects.append(mheads[0])
        
    def getMESH(self,subjblock):
        self.sMESH=""
        for mesh in self.subjects:
            self.sMESH += subjblock % mesh
        
    def setDOI(self,aidstr):
        if re.search('doi',aidstr):
            mflds=string.split(aidstr.strip(),' ')
            self.doi=mflds[0]
            
    def getDOI(self):
        if self.doi != "":
            return DOISTR % self.doi
        return ""
        
    def getPubmedLnk(self):
        return RETRIEVEURL % self.pmid
        
    def zapPunct(self,valu):
        return re.sub('[\.\?]$','',valu)
        
def doSearch(id):
    mysearch=SEARCHURL+'&id=%s' % (id)
    u=urllib.urlopen(mysearch)
    if u:
        lines=u.readlines()
        u.close()
        return lines
    return NULL
    
def genFields(refs, fieldsDict):
    Fields=""
    for kee in fieldsDict.keys():
        if fieldsDict[kee]() != "":
            Fields += FIELDSTR % (kee,fieldsDict[kee]())+"\n"
    return Fields
    
def emitDocument(fO,refs,fieldsDict):
    docinfo=ARTINFO % (refs.pmid, genFields(refs,fieldsDict))
    refs.getAuthors(AUTHBLOCK)
    refs.getMESH(SUBJSTR)
    docstr= DOCUBLOCK % (refs.getTitle(),refs.pubdate,refs.sAuthors,refs.sMESH,refs.getAbstract(ABSTSTR),docinfo)
    fO.write(docstr)
    
    
####################################
# main

refs=Ref()
fieldsDict= {'relation':refs.getPubmedLnk,'pubmedid':refs.getPmid,'publication_title':refs.getJournal,
'issn':refs.getISSN,'volnum':refs.getVol,'issnum':refs.getInum,'department':refs.getAddress,
'rights':refs.getCitation,'pages':refs.getPages}
parseDict= {'PMID':refs.setPmid, 'IS  ':refs.setISSN, 'VI  ':refs.setVol, 'IP  ':refs.setInum,
'EDAT':refs.setPubdate, 'TI  ': refs.setTitle, 'AB  ': refs.setAbstract, 'FAU ': refs.setAuthors,
'AID ':refs.setDOI, 'PG  ':refs.setPages,
'JT  ': refs.setJournal, 'MH  ':refs.setMESH,'SO  ':refs.setCitation,'AD  ':refs.setAddress,'AU  ': refs.setShortAuth}
fIDS=open(sys.argv[1])
if fIDS:
    fparts=string.split(sys.argv[1],'.')
    fOUT=open(fparts[0]+".xml","w")
    if fOUT:
        fOUT.write(HEAD)
        while 1:
            id=fIDS.readline()
            if not id: break
            pubs=doSearch(id.strip())
            for line in pubs:
                kee=line[:4]
                valu=re.sub('\&','and',line[6:].strip())
                if len(valu)<1: continue
                if parseDict.has_key(kee):
                    parseDict[kee](valu)
                    curState=kee
                if kee == '    ':
                    parseDict[curState](valu)
            emitDocument(fOUT,refs,fieldsDict)
            refs.__init__()
        fOUT.write(FOOTER)
        fOUT.close()
fIDS.close()




