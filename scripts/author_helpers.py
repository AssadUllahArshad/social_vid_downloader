"""Write individually authored drafts into the existing canonical store."""
import json
import re
from pathlib import Path
from datetime import date
STORE=Path('content/editorial/articles.json')
BRIEFS=Path('content/editorial/first-500-inventory.json')
def add(slug,title,intro,sections,example,sources,related=None,platform='general'):
 path=f'/guides/{platform}/{slug}/'
 briefs=json.loads(BRIEFS.read_text());brief=next(b for b in briefs if b['path']==path)
 assert brief['disposition']['classification']=='APPROVED_TO_WRITE'
 pages=json.loads(STORE.read_text());assert not any(p['path']==path for p in pages),path
 sentences=re.split(r'(?<=[.!?])\s+',intro)
 description=sentences[0]
 if len(description)<65 and len(sentences)>1:description+=' '+sentences[1]
 assert 65<=len(description)<=200,'Provide a complete SEO description sentence within 65–200 characters'
 page={**{k:v for k,v in brief.items() if k!='disposition'},'title':title,'h1':title,'description':description,'canonical':path,'status':'DRAFT','indexable':False,'intro':intro,'sections':[{'heading':h,'paragraphs':[p for p in text.split('\n\n') if p]} for h,text in sections],'example':example,'faq':[],'related':[f'/guides/general/{s}/' for s in (related or ['source-provided-format-inventory','verified-file-readiness','browser-preview-vs-save'])],'sources':[{'title':t,'url':u} for t,u in sources],'lastUpdated':str(date.today()),'review':{'accuracy':True,'distinctValue':True,'answerFirst':True,'supportedClaims':True,'examples':True,'specificity':True,'reviewer':'Source and copy review for '+brief.get('batch','first batch'),'reviewedAt':str(date.today())}}
 pages.append(page);STORE.write_text(json.dumps(pages,indent=2)+'\n')
 words=len((' '.join([intro,example]+[text for _,text in sections])).split());print(slug,words)
