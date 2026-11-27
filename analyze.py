"""Chronological validation. Reproduce: python build_data.py && python analyze.py && python build_site.py."""
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
P=Path(__file__).parent;D=P/'data'; d=json.loads((D/'dataset.json').read_text()); items={r['id']:r for r in d['items']}; papers=d['papers']; rng=np.random.default_rng(20261127); trials=5000
subjects=list(dict.fromkeys(p['subject'] for p in papers)); out={};
# Ties are randomized in expectation. No answer from a held-out paper is available to strategies,
# except simulated choices in the nonblank questions. Historical means computed only on earlier papers.
def hist(p,train):
 a=np.array([items[i]['answer']-1 for i in p['items']]); qs=[items[i]['question'] for i in p['items']]
 c=np.stack([np.bincount([items[i]['answer']-1 for i in t['items']],minlength=5) for t in train]); h=c.sum(0); h=(h==h.max()).astype(float); h/=h.sum()
 pos=np.zeros((len(qs),5))
 for t in train:
  lookup={items[i]['question']:items[i]['answer']-1 for i in t['items']}
  for j,q in enumerate(qs):
   if q in lookup:pos[j,lookup[q]]+=1
 pos=(pos==pos.max(1,keepdims=True)).astype(float);pos/=pos.sum(1,keepdims=True)
 return a,qs,c,h,pos
for s in subjects:
 pp=sorted([p for p in papers if p['subject']==s and p['status']=='과거' and p['exam']=='수능'],key=lambda p:p['year']); scenarios=[]
 for n in [1,3,5,10]:
  for ac in [.6,.7,.8,.9,.95,1.]:
   results=[]
   for p in pp:
    train=[t for t in pp if t['year']<p['year']]
    if len(train)<2:continue
    a,qs,c,h,pos=hist(p,train);N=len(a)
    if n>=N:continue
    order=rng.random((trials,N)).argsort(1); miss=order[:,:n]; known=order[:,n:]
    truth=a[miss]; seen=a[known]; seen=np.where(rng.random(seen.shape)<ac,seen,(seen+rng.integers(1,5,seen.shape))%5)
    count=(seen[:,:,None]==np.arange(5)).sum(1); least=count==count.min(1,keepdims=True); least=least/least.sum(1,keepdims=True)
    # Correct observed counts for symmetric error, then compare to prior mean total counts.
    # Positive deficits favor choices likely missing. This is a heuristic, not a calibrated posterior.
    chance=(1-ac)/4; corrected=(count-(N-n)*chance)/(ac-chance); deficits=c.mean(0)-corrected; top=np.isclose(deficits,deficits.max(1,keepdims=True));top=top/top.sum(1,keepdims=True)
    ii=np.arange(trials)[:,None]; vals=[.2,float(h[truth].mean()),float(pos[miss,truth].mean()),float(least[ii,truth].mean()),float(top[ii,truth].mean())]
    results.append({'year':p['year'],'train_years':[t['year'] for t in train],'rates':[round(v,6) for v in vals]})
   if results:scenarios.append({'blanks':n,'accuracy':ac,'mask':'random','rates':np.mean([r['rates'] for r in results],0).round(6).tolist(),'years':results})
 out[s]=scenarios
# iid count-spread comparator for matching paper lengths
ref={}
for n in [20,21,45]:
 x=rng.multinomial(n,[.2]*5,size=100000); spread=x.max(1)-x.min(1);ref[n]={'mean_spread':round(float(spread.mean()),4),'p_le_2':round(float((spread<=2).mean()),5)}
res={'trials':trials,'seed':20261127,'strategies':['무작위','과거 최빈 번호','문항별 과거 최빈','현재 최소 빈도','과거 평균 부족분'],'scenarios':out,'iid':ref}
(D/'analysis.json').write_text(json.dumps(res,ensure_ascii=False,separators=(',',':')))
for s,sc in out.items():
 r=next(r for r in sc if r['blanks']==5 and r['accuracy']==.9 and r['mask']=='random'); print(s, np.round(np.array(r['rates'])*100,1),len(r['years']))
