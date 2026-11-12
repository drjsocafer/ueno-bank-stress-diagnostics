"""Render publication charts from the executed outputs. Requires matplotlib."""
from pathlib import Path
import csv, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)
s=json.loads((ROOT/'results/summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,
 'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'#f6f7f5',
 'axes.facecolor':'#f6f7f5','text.color':'#123c40','axes.labelcolor':'#123c40',
 'xtick.color':'#34565a','ytick.color':'#34565a'})
colors=['#17646b','#97b4ad','#d7a45e']

fig,ax=plt.subplots(figsize=(12,6.4))
x=[0,1,2]; w=.33
for j,(term,color) in enumerate([(36,colors[0]),(60,colors[1])]):
 vals=[r['npl_ratio']*100 for r in s['cohort_core'] if r['term_months']==term]
 xs=[v+(j-.5)*w for v in x]
 bars=ax.bar(xs,vals,width=w,color=color,label=f'{term//12}-year maturity')
 ax.bar_label(bars,labels=[f'{v:.2f}%' for v in vals],padding=6,fontsize=12)
ax.axhline(.4,color='#a04a3b',ls='--',lw=1.6,label='Reported YE25 NPL: 0.4% (reference only)')
ax.set_xticks(x,['0%','46.4%','100%']); ax.set_xlabel('Assumed annual growth in new lending')
ax.set_ylabel('Simulated NPL / gross loans (%)'); ax.set_ylim(0,2.9)
ax.set_title('Fast growth changes the ratio. It does not identify credit quality.',loc='left',pad=25,fontsize=17)
ax.legend(frameon=False,loc='upper right',fontsize=11)
fig.subplots_adjust(left=.09,right=.97,top=.83,bottom=.25)
fig.text(.09,.115,'Synthetic cohort model | 6% lifetime default probability | 12-month NPL retention',fontsize=11)
fig.text(.09,.067,'Equal-principal amortisation; Weibull default timing (shape 2, scale 18 months). No bank calibration.',fontsize=10)
fig.savefig(FIG/'cohort_growth.png',dpi=180); fig.savefig(FIG/'cohort_growth.svg'); plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(12,6.4),gridspec_kw={'wspace':.35})
ax=axes[0]
g=[0,.1,.25]; val=[3,1.8,0]
b=ax.bar(['0%','10%','25%'],val,color=colors[0],width=.55)
ax.bar_label(b,labels=[f'{v:.1f}%' for v in val],padding=6)
ax.set_ylim(0,3.8); ax.set_ylabel('Correction budget / opening RWA (%)')
ax.set_xlabel('Assumed net increase in RWA'); ax.set_title('Capital correction budget',loc='left',fontsize=14,pad=18)
ax=axes[1]
r=[0,.05,.10,.20]; y=[.919/(1-v)*100 for v in r]
ax.plot([v*100 for v in r],y,'o-',color=colors[0],lw=2,ms=7)
ax.axhline(100,color='#a04a3b',ls='--',lw=1)
for xx,yy in zip(r,y): ax.annotate(f'{yy:.1f}%',(xx*100,yy),xytext=(0,9),textcoords='offset points',ha='center',fontsize=11)
ax.set_xlim(-1,21); ax.set_ylim(87,121); ax.set_xticks([0,5,10,20]); ax.set_ylabel('Loans / customer deposits (%)')
ax.set_xlabel('Assumed customer deposit runoff (%)'); ax.set_title('Static funding sensitivity',loc='left',fontsize=14,pad=18)
fig.suptitle('Capital and funding: two separate diagnostics',x=.08,ha='left',fontsize=18,fontweight='bold',y=.96)
fig.subplots_adjust(left=.08,right=.97,top=.78,bottom=.27)
fig.text(.08,.15,'Left: synthetic 15% opening capital ratio, 12% target, no scenario losses. This is not Ueno capital.',fontsize=10)
fig.text(.08,.115,'Right: June 2026 L/D of 91.9% (Fitch, 16 Oct). Hypothetical deposit outflows; loans unchanged.',fontsize=10)
fig.text(.08,.08,'Loans held constant; no asset sales, inflows or replacement funding. L/D above 100% is not a liquidity-failure test.',fontsize=10)
fig.savefig(FIG/'capital_funding.png',dpi=180); fig.savefig(FIG/'capital_funding.svg'); plt.close(fig)
print('Rendered 2 figures.')
