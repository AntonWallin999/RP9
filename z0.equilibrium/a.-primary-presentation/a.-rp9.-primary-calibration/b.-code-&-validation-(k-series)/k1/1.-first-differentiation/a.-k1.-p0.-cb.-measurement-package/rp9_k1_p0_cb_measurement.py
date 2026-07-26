#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, math, platform, sys
from fractions import Fraction
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.lines import Line2D

SCRIPT_NAME='RP9_K1_P0_Cb_MEASUREMENT.py'; VERSION='1.0.0'
R_EXACT=Fraction(1,1); D_EXACT=Fraction(1,1)
RI2_EXACT=R_EXACT**2-(D_EXACT/2)**2
RATIO_EXACT=RI2_EXACT/R_EXACT**2; LOCK_EXACT=1-RATIO_EXACT
R=float(R_EXACT); D=float(D_EXACT)
RI=math.sqrt(R*R-(D/2)**2); DR=R-RI
AY=math.pi*R*R; AI=math.pi*RI*RI
FLOAT_RATIO=AI/AY; FLOAT_LOCK=1-FLOAT_RATIO
RRES=FLOAT_RATIO-float(RATIO_EXACT); LRES=FLOAT_LOCK-float(LOCK_EXACT)

def utc_now(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def frac(v): return f'{v.numerator}/{v.denominator}'
def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1048576),b''): h.update(c)
    return h.hexdigest()

def datasheet():
    lp=RI/R*100; dp=DR/R*100
    tests={
      'R_positive':R>0,'D_positive':D>0,'self_relation_D_equals_R':D_EXACT==R_EXACT,
      'ri_squared_exact_3_over_4':RI2_EXACT==Fraction(3,4),'ri_smaller_than_R':RI<R,
      'area_ratio_exact_3_over_4':RATIO_EXACT==Fraction(3,4),'lock_exact_1_over_4':LOCK_EXACT==Fraction(1,4),
      'linear_percent_sum_100':math.isclose(lp+dp,100,abs_tol=1e-12),
      'area_percent_sum_100':math.isclose(float(RATIO_EXACT+LOCK_EXACT)*100,100,abs_tol=1e-12),
      'float_residuals_symmetric':math.isclose(RRES+LRES,0,abs_tol=1e-30)}
    return {
      'id':'K1_FIRST_DIFFERENTIATION_P0_C-b','name':'First Differentiation — Isolated Self-Relational Section',
      'version':VERSION,'generated_at_utc':utc_now(),'units':'dimensionless',
      'methodological_position':{'stage':'before explicit two-sphere Vesica Piscis presentation','classification':'isolated self-relational form measurement','relation':'D = R'},
      'input':{'R_exact':frac(R_EXACT),'D_exact':frac(D_EXACT),'R_float':R,'D_float':D},
      'derived_geometry':{'ri_formula':'sqrt(R^2 - (D/2)^2)','ri_symbolic':'sqrt(3)/2 * R','ri_squared_exact':frac(RI2_EXACT),'ri_float':RI,'delta_r':DR},
      'linear_relation':{'ri_over_R':RI/R,'ri_over_R_percent':lp,'delta_r_over_R':DR/R,'delta_r_over_R_percent':dp},
      'area_relation':{'ri_squared_over_R_squared_exact':frac(RATIO_EXACT),'AI_over_AY_exact':frac(RATIO_EXACT),'inner_percent':75.0,'differential_exact':frac(LOCK_EXACT),'differential_percent':25.0},
      'numerical_representation':{'exact_ratio':0.75,'exact_lock':0.25,'geometric_float_ratio':FLOAT_RATIO,'geometric_float_lock':FLOAT_LOCK,'ratio_residual':RRES,'lock_residual':LRES,'ratio_hex':FLOAT_RATIO.hex(),'lock_hex':FLOAT_LOCK.hex()},
      'verification':{'tests':tests,'total_status':'PASS' if all(tests.values()) else 'FAIL'}}

def panel(ax,x,y,w,h,title,lines):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=0.012',lw=1,ec=(1,1,1,.3),fc=(.03,.03,.03,.88),transform=ax.transAxes))
    ax.text(x+.02,y+h-.035,title,transform=ax.transAxes,color='white',fontsize=11,fontweight='bold',va='top')
    yy=y+h-.09
    for t,c,s in lines:
        ax.text(x+.02,yy,t,transform=ax.transAxes,color=c,fontsize=s,va='top',family='DejaVu Sans Mono'); yy-=.085

def make_png(path,dpi=180):
    fig=plt.figure(figsize=(16,9),facecolor='black')
    ax=fig.add_axes([.04,.30,.56,.62]); ax.set_facecolor('black'); ax.set_aspect('equal'); ax.set_xlim(-1.3,1.9); ax.set_ylim(-1.15,1.15); ax.axis('off')
    outer='#7f0f2f'; inner='#7c2d63'; cyan='#22d3ee'; yellow='#fde047'; white='#f8fafc'; center='#fbcfe8'
    ax.add_patch(Circle((0,0),R,fc=outer,ec='#9f1239',lw=2.2,alpha=.92))
    ax.add_patch(Circle((0,0),RI,fc=inner,ec=cyan,lw=2.8,alpha=.78)); ax.scatter([0],[0],s=58,color=center,zorder=8)
    ax.add_line(Line2D([0,0],[0,R],color=white,lw=2.2)); ax.add_line(Line2D([0,0],[0,-RI],color=cyan,lw=2.2))
    ax.scatter([0,0],[R,-RI],s=34,color=[white,cyan],zorder=8); ax.text(.08,.50,'R',color=white,fontsize=24,fontweight='bold'); ax.text(.08,-.43,r'$r_i$',color=cyan,fontsize=24,fontweight='bold')
    ax.plot([-R,-RI],[0,0],color=yellow,lw=3); ax.plot([-R,-R],[-.06,.06],color=yellow,lw=2); ax.plot([-RI,-RI],[-.06,.06],color=yellow,lw=2)
    ax.annotate('',xy=(-RI,.14),xytext=(-R,.14),arrowprops=dict(arrowstyle='<->',color=yellow,lw=1.8)); ax.text(-(R+RI)/2,.22,r'$\Delta r$',color=yellow,fontsize=20,ha='center')
    ax.plot([0,1.18],[R,R],color=(1,1,1,.45),lw=1,ls='--'); ax.text(1.22,1.02,'OUTER RADIUS',color='white',fontsize=12,fontweight='bold'); ax.text(1.22,.91,f'R = {R:.16f}',color='white',fontsize=11,family='DejaVu Sans Mono')
    ax.plot([RI,1.18],[0,0],color=cyan,lw=1,ls='--'); ax.text(1.22,.08,'INNER RADIUS',color=cyan,fontsize=12,fontweight='bold'); ax.text(1.22,-.04,r'$r_i = \sqrt{3}/2 \cdot R$',color=cyan,fontsize=11); ax.text(1.22,-.15,f'= {RI:.16f}',color=cyan,fontsize=11,family='DejaVu Sans Mono')
    ax.plot([RI,1.18],[-.55,-.55],color=yellow,lw=1,ls='--'); ax.text(1.22,-.47,'RADIAL DIFFERENCE',color=yellow,fontsize=12,fontweight='bold'); ax.text(1.22,-.59,r'$\Delta r = R-r_i$',color=yellow,fontsize=11); ax.text(1.22,-.70,f'= {DR:.16f}',color=yellow,fontsize=11,family='DejaVu Sans Mono')
    fig.text(.045,.955,'K1. FIRST DIFFERENTIATION — P(0)(C-b)',color='white',fontsize=22,fontweight='bold'); fig.text(.045,.922,'ISOLATED SELF-RELATIONAL SECTION WITH MEASUREMENTS',color='#cbd5e1',fontsize=13)
    pa=fig.add_axes([.035,.035,.93,.24]); pa.set_facecolor('black'); pa.axis('off')
    panel(pa,0,.05,.31,.88,'LINEAR RELATION',[(f'ri / R = {RI/R:.16f}','#22d3ee',8.5),(f'       = {(RI/R)*100:.14f} %','#22d3ee',8.5),(f'Δr / R = {DR/R:.16f}','#fde047',8.5),(f'       = {(DR/R)*100:.14f} %','#fde047',8.5)])
    panel(pa,.335,.05,.31,.88,'AREA / SQUARED RELATION',[('ri² / R² = 3/4 = 0.75','#22d3ee',8.5),('AI / AY   = 3/4 = 0.75','#22d3ee',8.5),('Inner relation = 75 %','#22d3ee',8.5),('Differential   = 25 %','#fde047',8.5)])
    panel(pa,.67,.05,.33,.88,'NUMERICAL REPRESENTATION',[('EXACT','#4ade80',8.5),('Ratio = 0.75','#4ade80',8),('Lock  = 0.25','#4ade80',8),('FLOAT — GEOMETRIC PATH','#fbbf24',8.5),(f'Ratio = {FLOAT_RATIO:.16f}','#fbbf24',8),(f'Lock  = {FLOAT_LOCK:.16f}','#fbbf24',8),(f'Ratio residual = {RRES:.17e}','#e5e7eb',7.2),(f'Lock residual  = {LRES:.17e}','#e5e7eb',7.2)])
    fig.text(.5,.012,'ISOLATED FORM MEASUREMENT BEFORE THE FULL TWO-SPHERE VESICA PISCIS PRESENTATION.',color='#d1d5db',fontsize=9,ha='center')
    fig.savefig(path,dpi=dpi,facecolor='black',bbox_inches='tight',pad_inches=.12); plt.close(fig)

def markdown(d):
    l=d['linear_relation']; n=d['numerical_representation']
    return f'''# K1. FIRST DIFFERENTIATION — P(0)(C-b)\n\n## Isolated Self-Relational Section\n\n---\n\n## 1. Purpose\n\nThis presentation isolates the first measurable differentiation within the spherical form before the full two-sphere Vesica Piscis configuration is displayed.\n\nThe self-relation is defined by $D=R$. The derived internal circle is:\n\n$$\nr_i=\\sqrt{{R^2-\\left(\\frac{{D}}{{2}}\\right)^2}}=\\frac{{\\sqrt{{3}}}}{{2}}R\n$$\n\n## 2. Linear Measurement\n\n| Measurement | Value |\n|---|---:|\n| $R$ | `{R:.16f}` |\n| $r_i$ | `{RI:.16f}` |\n| $r_i/R$ | `{l['ri_over_R']:.16f}` |\n| Inner linear relation | `{l['ri_over_R_percent']:.14f}%` |\n| $\\Delta r/R$ | `{l['delta_r_over_R']:.16f}` |\n| Linear differential | `{l['delta_r_over_R_percent']:.14f}%` |\n\n## 3. Area / Squared-Radius Measurement\n\n$$\n\\frac{{r_i^2}}{{R^2}}=\\frac{{A_I}}{{A_Y}}=\\frac34\n$$\n\n| Relation | Exact | Percentage |\n|---|---:|---:|\n| Inner | $3/4$ | 75% |\n| Differential | $1/4$ | 25% |\n\nThe visible radial gap is the linear difference $1-\\sqrt{{3}}/2$, not 25%. The 75/25 relation belongs to squared radius and area.\n\n## 4. Numerical Representation\n\n```text\nExact ratio = 0.75\nExact lock  = 0.25\nFloat ratio = {n['geometric_float_ratio']:.16f}\nFloat lock  = {n['geometric_float_lock']:.16f}\nRatio residual = {n['ratio_residual']:.17e}\nLock residual  = {n['lock_residual']:.17e}\n```\n\n## 5. Verification Status\n\n```text\n{d['verification']['total_status']}\n```\n'''

def verify_log(d):
    t=d['verification']['tests']; lines=['K1. FIRST DIFFERENTIATION — P(0)(C-b) — VERIFICATION LOG','='*78,f"Generated UTC : {d['generated_at_utc']}",f'Script        : {SCRIPT_NAME}',f'Version       : {VERSION}',f'Python        : {sys.version.split()[0]}',f'Platform      : {platform.platform()}','',f'R = {R:.16f}',f'D = {D:.16f}',f'ri = {RI:.16f}',f'delta_r = {DR:.16f}',f'ri/R = {RI/R:.16f}',f'delta_r/R = {DR/R:.16f}',f'ri^2/R^2 = {frac(RATIO_EXACT)}',f'AI/AY = {frac(RATIO_EXACT)}',f'Float ratio = {FLOAT_RATIO:.16f}',f'Float lock = {FLOAT_LOCK:.16f}',f'Ratio residual = {RRES:.17e}',f'Lock residual = {LRES:.17e}','','TESTS','-'*78]
    lines += [f'{k:<46} {"PASS" if v else "FAIL"}' for k,v in t.items()]
    lines += ['','='*78,f"TOTAL STATUS: {d['verification']['total_status']}",'='*78]
    return '\n'.join(lines)+'\n'

def generate(dpi=180):
    base=Path(__file__).resolve().parent; out=base/'OUTPUT'; out.mkdir(exist_ok=True); d=datasheet(); stem='K1_FIRST_DIFFERENTIATION_P0_C-b'
    p={'png':out/f'{stem}.png','json':out/f'{stem}.json','markdown':out/f'{stem}.md','verification_log':out/f'{stem}_VERIFY.log'}
    make_png(p['png'],dpi); p['json'].write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8'); p['markdown'].write_text(markdown(d),encoding='utf-8'); p['verification_log'].write_text(verify_log(d),encoding='utf-8')
    manifest=out/f'{stem}_MANIFEST.json'; manifest.write_text(json.dumps({'script':SCRIPT_NAME,'version':VERSION,'generated_at_utc':utc_now(),'files':{k:{'name':v.name,'bytes':v.stat().st_size,'sha256':sha256(v)} for k,v in p.items()}},indent=2),encoding='utf-8'); p['manifest']=manifest
    return p

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dpi',type=int,default=180); a=ap.parse_args(); files=generate(a.dpi); print('\n'.join(f'{k}: {v}' for k,v in files.items()))
if __name__=='__main__': main()
