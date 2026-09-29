import importlib.util, json, sys, collections, re, textwrap
sys.path.insert(0,'share')
src=sys.argv[1]
if src=='gen':
    spec=importlib.util.spec_from_file_location('g','share/gen_curriculum_v2.py'); g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g); cur=g.build()
else:
    cur=json.load(open(src))
import v2_runtime as rt
Q=cur['questions']; print('rev',cur.get('revision'),'cards',len(cur['cards']),'questions',len(Q))
lf=collections.Counter(q.get('learning_form',q['form']) for q in Q); print('learning_form',dict(lf))
JARGON=["named change","named defect","registered","stated scope","bounded","scope","registration contract","acting region","the module's"]
def halves(c):
    if ' | NEOVIM: ' in c: a,n=c.split(' | NEOVIM: ',1); return a.replace('ANIMATION: ',''),n
    return None,c
tmpl=0; jar=collections.Counter(); ident_compact=0; ident80=0; leak=0; fixed_pred=collections.Counter(); ex=[]
for q in Q:
    ch=q['choices']
    if any('makes only its named change' in c for c in ch): tmpl+=1
    for c in ch:
        for j in JARGON:
            if j in c: jar[j]+=1
    comp=[rt._compact_choice_text(c) for c in q.get('compact_choices',ch)]
    if len(set(comp))<len(comp): ident_compact+=1
    # distinguishing text visible in the compact left half?
    lefts=[x.split(' · V: ')[0] for x in comp if ' · V: ' in x]
    if lefts and len(set(lefts))==1 and len(set(halves(c)[0] for c in ch))>1: ident80+=1; ex.append(q['id'])
    # pattern leak: correct answer identifiable by template phrase alone
    cc=ch[q['correct_choice']]
    if 'makes only its named change' in cc or cc.startswith('It made the stated bounded edit') or cc.startswith('TARGET exactly; only the acting'): leak+=1
    if q.get('learning_form',q['form'])=='predict_art' or q['form']=='predict_art':
        fixed_pred[tuple(ch)]+=1
print('template-generated paired choices (named change/defect):',tmpl)
print('jargon phrase hits in choices:',dict(jar))
print('questions whose 4 compact choices are not all distinct:',ident_compact)
print('questions whose compact ANIMATION half is identical across choices but full halves differ:',ident80, ex[:8])
print('correct answer detectable from boilerplate wording alone:',leak)
print('reused identical predict_art choice sets:',[(n) for s,n in fixed_pred.most_common(3)])
# 80-col full-layout clipping: lines longer than popup inner width (80*0.9-2 ~ 70)
w=70; long=sum(1 for q in Q for c in q['choices'] if len('  a) '+c)>w); print('full-layout choice lines >70 cols:',long,'of',sum(len(q['choices']) for q in Q))
q=[x for x in Q if x['id']==(ex[0] if ex else Q[0]['id'])][0]
print('\nEXAMPLE',q['id'],q.get('learning_form')); print(q['prompt'][:400]); [print(' -',c) for c in q['choices']]; print('compact:'); [print(' -',rt._compact_choice_text(c)) for c in q.get('compact_choices',[])]
