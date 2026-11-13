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

# The two numbered figures used in the revised LinkedIn article.
with (ROOT/'results/growth_transition.csv').open() as f:
 transition=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(12,6.4))
xx=[float(r['years']) for r in transition]
yy=[float(r['npl_ratio'])*100 for r in transition]
ax.plot(xx,yy,color=colors[0],lw=2.5)
ax.axvline(0,color='#738a86',lw=1.2,ls='--')
ax.text(.03,2.44,'Origination growth changes',fontsize=10)
ax.scatter([xx[0],xx[-1]],[yy[0],yy[-1]],color=colors[0],s=30)
ax.annotate(f'{yy[0]:.2f}%',(xx[0],yy[0]),xytext=(0,12),textcoords='offset points',ha='left')
ax.annotate(f'{yy[-1]:.2f}%',(xx[-1],yy[-1]),xytext=(0,12),textcoords='offset points',ha='right')
ax.set_xticks([-1,0,1,2,3,4]); ax.set_ylim(0,2.65)
ax.set_ylabel('Simulated NPL / gross loans (%)'); ax.set_xlabel('Years since origination growth changed to 0%')
ax.set_title('When growth stops, the NPL ratio can rise.',loc='left',pad=25,fontsize=18)
fig.subplots_adjust(left=.09,right=.97,top=.83,bottom=.26)
fig.text(.09,.135,'Figure 1 | Annual origination growth 46.4% before month 0, then constant monthly new lending.',fontsize=10)
fig.text(.09,.09,'3-year loans; lifetime PD 6%; NPL retention 12 months; Weibull timing (shape 2, scale 18 months).',fontsize=10)
fig.text(.09,.045,'Credit quality is unchanged. Portfolio composition changes. Synthetic model; no bank calibration.',fontsize=10)
fig.savefig(FIG/'figure_1_growth_transition.png',dpi=180)
fig.savefig(FIG/'figure_1_growth_transition.svg'); plt.close(fig)

with (ROOT/'results/non_identification.csv').open() as f:
 fits=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(12,6.4))
for i,window in enumerate([3,6,12,24]):
 rows=[r for r in fits if int(r['retention_months'])==window]
 vals=[float(r['implied_lifetime_pd'])*100 for r in rows]
 ax.plot([min(vals),max(vals)],[i,i],color='#a7b9b4',lw=3)
 ax.scatter(vals,[i]*3,color=colors[0],s=40,zorder=3)
 ax.text(min(vals)-.1,i,f'{min(vals):.1f}%',ha='right',va='center',fontsize=11)
 ax.text(max(vals)+.1,i,f'{max(vals):.1f}%',ha='left',va='center',fontsize=11)
ax.set_yticks(range(4),['3 months','6 months','12 months','24 months']); ax.invert_yaxis()
ax.set_xlim(0,7.4); ax.set_ylim(3.5,-.7)
ax.set_xlabel('Implied lifetime default probability (%)')
ax.set_ylabel('Time defaulted principal stays in the gross book')
ax.set_title('One reported ratio, many possible credit qualities',loc='left',pad=25,fontsize=17)
fig.subplots_adjust(left=.19,right=.97,top=.83,bottom=.25)
fig.text(.19,.13,'Figure 2 | PD values consistent with 0.4% NPL stock; 3-year loans; 46.4% origination growth.',fontsize=10)
fig.text(.19,.08,'Each row uses Weibull timing scales 9, 18 and 30 months (shape 2); equal-principal amortisation.',fontsize=10)
fig.text(.19,.035,'Alternative configurations, not a confidence interval or estimates of any bank\'s true default rate.',fontsize=10)
fig.savefig(FIG/'figure_2_non_identification.png',dpi=180)
fig.savefig(FIG/'figure_2_non_identification.svg'); plt.close(fig)
print('Rendered article Figures 1 and 2 from the published CSV data.')
