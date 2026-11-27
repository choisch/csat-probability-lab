from pathlib import Path
P=Path(__file__).parent
s=(P/'template.html').read_text();s=s.replace('__DATASET__',(P/'data/dataset.json').read_text().replace('</','<\\/')).replace('__ANALYSIS__',(P/'data/analysis.json').read_text().replace('</','<\\/'));(P/'index.html').write_text(s)
print('built',len(s),'characters')
