"""Reproducible exportable scientific figure; descriptive uncertainty, not causal lift."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
def plot(root):
    df=pd.read_csv(root/'reports/repeat_purchase_statistics.csv')
    order=['1 SKU','2-5 SKUs','6+ SKUs'];df=df.set_index('breadth_group').loc[order]
    fig,ax=plt.subplots(figsize=(10,5.5),layout='constrained')
    fig.set_facecolor('#edf2f2');ax.set_facecolor('#edf2f2')
    x=range(3);p=df.repeat_90d_rate
    ax.errorbar(x,p,yerr=[p-df.ci95_lower,df.ci95_upper-p],fmt='o',capsize=7,color='#007f79',markersize=11,linewidth=2)
    for i,(_,r) in enumerate(df.iterrows()):
        ax.annotate(f'{r.repeat_90d_rate:.1%}\nn={int(r.eligible_customers):,}',(i,r.ci95_upper),xytext=(0,10),textcoords='offset points',ha='center',fontsize=11,color='#153445')
    ax.set_xticks(list(x),order);ax.set_ylim(0,.75);ax.set_xlim(-.4,2.4);ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylabel('Customers with a second order within 90 days',color='#153445',labelpad=12)
    ax.set_xlabel('Distinct merchandise SKUs in first observed order',labelpad=12,color='#153445')
    ax.set_title('First-basket breadth and repeat purchasing',loc='left',fontweight='bold',color='#153445',fontsize=17,pad=28)
    ax.grid(axis='y',color='#d7e2e5');ax.set_axisbelow(True)
    for s in ax.spines.values():s.set_visible(False)
    ax.tick_params(colors='#5b707b',length=0)
    fig.supxlabel('Descriptive 95% Wilson intervals · mature observed cohorts after warmup\nObservational association; customer intent and purchase history may confound the pattern.',fontsize=10,color='#5b707b')
    for ext in ['png','svg']:fig.savefig(root/f'assets/repeat_purchase_uncertainty.{ext}',dpi=180)
    plt.close(fig)
if __name__=='__main__':plot(Path(__file__).resolve().parents[1])
