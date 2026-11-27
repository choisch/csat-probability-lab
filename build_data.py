import csv,json
from pathlib import Path
from collections import defaultdict
P=Path(__file__).parent; D=P/'data'; D.mkdir(exist_ok=True)
# Academic year, question order; MC only. Source transcription, not an official certified corpus.
core={
2022: ['25113 43232 55442 41332 41443 55213 5453','45411 31225 3','52215 43445 3','25541 31145 33232','441321','542312','235245'],
2023: ['45145 32524 52534 41433 51533 41512 1423','15344 32452 1','24141 21354 3','54135 24434 12315','325324','435422','534212'],
2024: ['53153 22315 23144 54213 52133 25141 2234','45445 13325 1','44134 21533 5','14214 45242 13113','345224','324312','432535'],
2025: ['34545 32123 15312 23241 44522 11435 4352','24345 43115 2','54312 43521 3','54524 53143 21542','531332','342112','343114'],
2026: ['35414 25355 31151 23243 25144 25513 2413','25312 54432 5','32441 24524 3','14533 25143 32544','312542','343125','315244'],
2027: ['14323 53214 25313 53215 41453 52542 1244','15533 51342 4','52534 12153 4','25341 12342 53243','325513','141534','343514'],
}
# Transcribed answer sequences
other={
'한국사': {2022:'53545 34322 13124 15353',2023:'14441 23234 33552 35355',2024:'52512 23124 34141 52453',2025:'51331 45253 54132 24321',2026:'33152 54531 32453 52214'},
'생활과 윤리':{2022:'32152 21354 22353 41554',2023:'31214 44555 31232 24345',2024:'14152 43414 43522 42335',2025:'42555 33444 12131 43255',2026:'22253 45211 54413 35334'},
'윤리와 사상':{2022:'42355 12125 25412 33343',2023:'51255 22443 33143 41541',2024:'13251 44322 54351 42514',2025:'13454 55134 43225 55241',2026:'53334 13425 34144 52432'},
'생명과학Ⅰ':{2022:'54154 32334 22512 51441',2023:'53554 34121 32321 44214',2024:'33115 45225 41442 35534',2025:'51421 33242 54251 42315',2026:'54134 33551 12245 12152'},
'지구과학Ⅰ':{2022:'11332 54245 53213 52341',2023:'53235 42314 14312 52255',2024:'45513 43215 33214 53255',2025:'45434 22311 35251 55242',2026:'34451 52135 23125 14125'},
}
mocks=[(2022,'6월 모평','51132 42343 14512 53311 24412 35554 32244 15253 32325'),(2022,'9월 모평','51231 43544 51215 34231 21533 52434 32143 52451 25414'),(2026,'6월 모평','25544 31441 53313 24112 31324 25235 51424 43452 15335')]
rows={}; papers=[]
def src(y,m=11):return f'https://gichulbada.kr/round/H3_{(y-1)%100:02d}{m:02d}'
def engsrc(y,m=11):return f'https://gichulbada.kr/exam/H3_{(y-1)%100:02d}{m:02d}'
def seq(s):return [int(c) for c in str(s) if c in '12345']
def add(y,subject,block,questions,answers,source,kind='수능',form='대표형(형태 미확인)',points=None):
 a=seq(answers) if isinstance(answers,str) else answers; q=list(questions); assert len(a)==len(q),(y,subject,block,len(a),len(q)); ids=[]
 for i,(num,v) in enumerate(zip(q,a)):
  k=f'{y}|{kind}|{block}|{num}'
  row=dict(id=k,academic_year=y,exam=kind,block=block,question=num,answer=v,status='잠정' if y==2027 else '과거',form=form,source=source,points=points[i] if points else None)
  if k in rows:assert rows[k]==row,(k,rows[k],row)
  rows[k]=row;ids.append(k)
 return ids
def paper(y,subject,ids,kind='수능'):
 r=[rows[i] for i in ids]; assert len({v['question'] for v in r})==len(r); papers.append(dict(id=f'{y}|{kind}|{subject}',year=y,exam=kind,subject=subject,status=r[0]['status'],items=ids,form=r[0]['form']))
for y,v in core.items():
 ksource={2026:'https://wdown.ebsi.co.kr/W61001/01exam/20251113/go3/live_main_answer_1_kor_8ZE3E1XR.pdf',2027:'https://wdown.ebsi.co.kr/W61001/01exam/20261119/go3/live_main_answer_1_kor_M6WL13KA.pdf'}.get(y,src(y))
 kform='홀수형' if y in (2026,2027) else '대표형(형태 미확인)'
 k=add(y,'국어','국어 공통',range(1,35),v[0],ksource,form=kform)
 for n,a in zip(['화법과 작문','언어와 매체'],v[1:3]):paper(y,'국어 · '+n,k+add(y,n,n,range(35,46),a,ksource,form=kform))
 msource={
  2025:'https://image.donga.com/education/exam/2025_su/su-2025-neung_2a.pdf',
  2027:'https://wdown.ebsi.co.kr/W61001/01exam/20261119/go3/live_main_answer_1_math_4V462R5Q.pdf'
 }.get(y,src(y))
 f='홀수형' if y in (2025,2027) else '대표형(형태 미확인)'
 m=add(y,'수학','수학 공통',range(1,16),v[3],msource,form=f,points=[2]*2+[3]*6+[4]*7 if y==2025 else None)
 for n,a in zip(['확률과 통계','미적분','기하'],v[4:]):paper(y,'수학 · '+n,m+add(y,n,n,range(23,29),a,msource,form=f,points=[2,3,3,3,3,4] if y==2025 else None))
for s,ys in other.items():
 for y,a in ys.items():
  source=src(y)
  f='대표형(형태 미확인)' if s=='한국사' else '단일형'
  if (s in ('생명과학Ⅰ','지구과학Ⅰ')) or y in (2022,2025):
   slugs={'한국사':'korean-history','생활과 윤리':'life-ethics','윤리와 사상':'ethics-thought','생명과학Ⅰ':'biology-1','지구과학Ⅰ':'earth-science-1'}
   source=f'https://www.haksi.kr/exams/{y}11/{slugs[s]}'
   if s=='한국사':
    f='홀수형'
    if y==2025:source+='-odd'
  paper(y,s,add(y,s,s,range(1,21),a,source,form=f))
seed=defaultdict(list)
with (D/'english_seed.csv').open(encoding='utf-8-sig') as f:
 for r in csv.DictReader(f):seed[int(r['academic_year'])].append((int(r['question']),int(r['answer']),r['source']))
for y,rs in seed.items():
 rs=sorted(rs);paper(y,'영어',add(y,'영어','영어',[r[0] for r in rs],[r[1] for r in rs],rs[0][2],form='홀수형' if y in [2022,2024] else '대표형(형태 미확인)'))
for y,k,a in mocks:
 paper(y,'영어',add(y,'영어','영어',range(1,46),a,engsrc(y,6 if k.startswith('6') else 9),kind=k,form='단일형(자료 표기 미확인)'),kind=k)
# Additional older English papers, individually sourced. Answer groups follow question order.
extra_english={
2018: ('21423 51134 52315 25324 54544 35225 12113 34441 51343',engsrc(2018), '대표형(형태 미확인)'),
2019: ('341124522454 451353111441 345425312243 533132252','https://file.mk.co.kr/suneung/2019/3_1_a.pdf', '홀수형'),
2020: ('12133 44523 44225 13511 51524 53444 21123 52435 54323',engsrc(2020), '대표형(형태 미확인)'),
2021: ('511512343431 241551212132 554455231232 544334354','https://search1.daumcdn.net/search/statics/special/suneung_2021/2020_3_1.pdf', '홀수형'),
}
for y,(a,source,f) in extra_english.items():
 paper(y,'영어',add(y,'영어','영어',range(1,46),a,source,form=f))
# Paired forms are a separate comparison dataset, not independent questions or training papers.
paired={
2021:('113512143413 421553122123 554455232532 544334354','https://www.scribd.com/document/1065156888/3'),
2022:('542424133414 351253151215 434343215242 554123332','https://www.scribd.com/document/632467958/2022'),
2024:('152323234251 155435114241 423324125434 434125533','https://www.scribd.com/document/1039204163/2024'),
}
forms=[]
for y,(a,source) in paired.items():
 p=next(p for p in papers if p['year']==y and p['subject']=='영어' and p['exam']=='수능')
 odd=[rows[i]['answer'] for i in p['items']];even=seq(a);assert len(odd)==len(even)==45
 forms.append(dict(year=y,subject='영어',odd=odd,even=even,odd_source=rows[p['items'][0]]['source'],even_source=source))
(D/'form_comparison.json').write_text(json.dumps(forms,ensure_ascii=False,indent=2))

# verify structure, exclude short answers, mark sources
assert len(rows)==len(set(rows));assert all(1<=r['answer']<=5 for r in rows.values())
for p in papers:
 rs=[rows[i] for i in p['items']]; qs=[r['question'] for r in rs]
 assert qs==sorted(qs)
 assert len(rs)==(21 if p['subject'].startswith('수학') else 45 if p['subject'].startswith('국어') or p['subject']=='영어' else 20)
with (D/'answers.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(next(iter(rows.values()))));w.writeheader();w.writerows(rows.values())
(D/'papers.json').write_text(json.dumps(papers,ensure_ascii=False,indent=2))
(D/'dataset.json').write_text(json.dumps({'items':list(rows.values()),'papers':papers,'forms':forms},ensure_ascii=False,separators=(',',':')))
print('items',len(rows),'papers',len(papers),'subjects',len(set(p['subject'] for p in papers)),'historical',sum(r['status']=='과거' for r in rows.values()))
