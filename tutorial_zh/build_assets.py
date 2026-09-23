"""Build Chinese figures and TeX tables from the supplied saved results.

Only writes inside tutorial_zh. Requires NumPy and Matplotlib.
"""
from pathlib import Path
import csv
import json
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'assets'
OUT.mkdir(exist_ok=True)
font = Path.home() / 'Library/Fonts/NotoSansCJKsc-Regular.otf'
if font.exists():
    font_manager.fontManager.addfont(str(font))
    family = font_manager.FontProperties(fname=str(font)).get_name()
else:
    family = 'sans-serif'
plt.rcParams.update({'font.family': family, 'font.size': 10,
                     'axes.unicode_minus': False, 'axes.spines.top': False,
                     'axes.spines.right': False, 'pdf.fonttype': 42,
                     'axes.labelsize': 10, 'legend.fontsize': 8})
BLUE, RED, GREEN = '#236C86', '#BF5A36', '#588264'

def save(fig, name):
    fig.savefig(OUT / (name + '.pdf'), bbox_inches='tight')
    plt.close(fig)

def read_csv(name):
    with (ROOT / 'results' / name).open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def table(name, caption, label, header, body, spec):
    text = '\\begin{table}[htbp]\\centering\\small\n'
    text += '\\caption{' + caption + '}\\label{' + label + '}\n'
    text += '\\begin{tabular}{' + spec + '}\\toprule\n'
    text += ' & '.join(header) + '\\\\\\midrule\n'
    text += '\n'.join(' & '.join(row) + '\\\\' for row in body)
    text += '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    (OUT / (name + '.tex')).write_text(text, encoding='utf-8')

g = read_csv('gbm_convergence.csv')
na = json.loads((ROOT / 'results/nonaffine_summary.json').read_text())
gs = json.loads((ROOT / 'results/gbm_summary.json').read_text())

y = np.linspace(-5, 5, 400)
fig, axes = plt.subplots(1, 3, figsize=(10.3, 3.2), layout='constrained')
axes[0].plot(y, .1+.4/(1+np.exp(-y)), color=BLUE)
axes[0].axhline(.1, color='gray', ls=':', lw=.8)
axes[0].axhline(.5, color='gray', ls=':', lw=.8)
axes[0].scatter([0],[.3], color=RED, s=18)
axes[0].set(title='资产波动率 g(y)', xlabel='因子 y', ylim=(.07,.53))
axes[1].plot(y, 2*(-.2-y), color=GREEN)
axes[1].axhline(0, color='gray', lw=.8)
axes[1].axvline(-.2, color='gray', ls=':', lw=.8)
axes[1].set(title='因子漂移：2(-0.2-y)', xlabel='因子 y')
axes[2].plot(y, .6*np.sqrt(1+y*y), color=RED)
axes[2].set(title='因子扩散幅度', xlabel='因子 y', ylabel=r'$0.6\sqrt{1+y^2}$')
save(fig, 'model_functions')

rng = np.random.default_rng(20260912)
dw = rng.normal(0, np.sqrt(1/256), (3,256))
w = np.column_stack((np.zeros(3), np.cumsum(dw,axis=1)))
fig, axes = plt.subplots(1,2,figsize=(10.3,3.5),layout='constrained')
t = np.linspace(0,1,257)
for j,c in enumerate([BLUE,RED,GREEN]):
    axes[0].plot(t,w[j],lw=1.1,color=c,label=f'样本路径 {j+1}')
axes[0].set(xlabel='时间 t',ylabel=r'$W_t$',title='同一模型可以产生不同路径')
axes[0].legend()
axes[1].plot(t,w[0],color=BLUE,lw=1,label='细网格：256 步')
axes[1].plot(t[::32],w[0,::32], 'o--',color=RED,ms=4,label='粗网格：8 步')
axes[1].set(xlabel='时间 t',ylabel=r'$W_t$',title='粗细网格在共同时间点完全一致')
axes[1].legend()
save(fig,'brownian_coupling')

fig, axes = plt.subplots(1,2,figsize=(10.3,3.9),layout='constrained')
for method,c,marker in [('EM',BLUE,'o'),('Milstein',RED,'s')]:
    r = [x for x in g if x['method']==method]
    h = np.array([float(x['h']) for x in r])
    e = np.array([float(x['strong_l1']) for x in r])
    axes[0].errorbar(h,e,yerr=[1.96*float(x['strong_se']) for x in r],fmt=marker+'-',color=c,ms=3,capsize=2,label=method)
    weak = -np.array([float(x['weak_bias_cv']) for x in r])
    axes[1].plot(h,weak,marker+'-',color=c,ms=3,label=method+'：控制后')
axes[1].plot(h,[-float(x['analytic_mean_bias']) for x in r],':',color='black',label='解析均值偏差的绝对值')
for ax in axes:
    ax.set(xscale='log',yscale='log',xlabel='步长 h')
    ax.legend(); ax.grid(alpha=.2)
axes[0].set(title='强误差：半阶与一阶',ylabel='终值平均绝对误差')
axes[1].set(title='弱偏差：两种方法均为一阶',ylabel='均值偏差的绝对值')
save(fig,'gbm_results_zh')

fig, axes = plt.subplots(1,2,figsize=(10.3,4.0),layout='constrained')
for ref,c in [(2048,RED),(4096,GREEN),(8192,BLUE)]:
    r = [x for x in na['convergence'] if x['reference_steps']==ref]
    h = np.array([x['h'] for x in r])
    e = np.array([x['strong_l1']['mean'] for x in r])
    axes[0].plot(h,e,'o-',ms=3,color=c,label=f'参考 {ref} 步')
axes[0].set(xscale='log',yscale='log',xlabel='粗步长 h',ylabel='与参考的平均绝对差',title='强差：参考仍是数值解')
axes[0].legend(); axes[0].grid(alpha=.2)
r = [x for x in na['convergence'] if x['reference_steps']==8192]
axes[1].errorbar(range(6),[x['weak_payoff_difference']['mean'] for x in r],
                 yerr=[1.96*x['weak_payoff_difference']['standard_error'] for x in r],
                 fmt='o-',color=BLUE,ms=4,capsize=4)
axes[1].axhline(0,ls='--',color=RED,lw=1)
axes[1].set(xticks=range(6),xticklabels=[f'1/{x["n_steps"]}' for x in r],xlabel='粗步长 h',ylabel='有符号收益均值差',title='弱差：误差棒为逐点 95% 区间')
axes[1].grid(axis='y',alpha=.2)
save(fig,'nonaffine_results_zh')

shutil.copy2(ROOT/'figures/gbm_distribution.pdf', OUT/'gbm_distribution.pdf')
shutil.copy2(ROOT/'figures/gbm_paths.pdf', OUT/'gbm_paths.pdf')

by = {(r['method'],int(r['N'])):r for r in g}
rows=[]
for n in [8,16,32,64,128,256,512,1024]:
    em,mi = by['EM',n],by['Milstein',n]
    rows.append([str(n),f'{float(em["strong_l1"]):.6f}',f'{1.96*float(em["strong_se"]):.6f}',f'{float(mi["strong_l1"]):.6f}',f'{1.96*float(mi["strong_se"]):.6f}'])
table('gbm_strong_zh','GBM 的终值强误差。半宽指 95\\% 蒙特卡洛区间半宽；正式路径数为 160000。','tab:results-gbm-strong',['$N$','EM 强误差','区间半宽','Milstein 强误差','区间半宽'],rows,'rrrrr')
rows=[]
for n in [8,16,32,64,128,256,512,1024]:
    em,mi=by['EM',n],by['Milstein',n]
    rows.append([str(n),f'{float(em["analytic_mean_bias"]):.8f}',f'{float(em["weak_bias_cv"]):.8f}',f'{float(mi["weak_bias_cv"]):.8f}'])
table('gbm_weak_zh','GBM 的有符号均值偏差：数值减精确。控制后结果仍是模拟估计，解析列是独立核对目标。','tab:results-gbm-weak',['$N$','解析偏差（两方法）','EM 控制后估计','Milstein 控制后估计'],rows,'rrrr')
q=read_csv('gbm_quantiles.csv')
rows=[[f'{float(x["probability"]):g}']+[f'{float(v):.3f}' for k,v in x.items() if k!='probability'] for x in q]
table('gbm_quantiles_zh','GBM 在粗网格 $h=1/8$ 上的分位数。精确模拟列也具有有限样本波动。','tab:results-quantiles',['概率 $p$','理论分位数','精确模拟','EM','Milstein'],rows,'rrrrr')
rows=[]
for x in na['convergence']:
    if x['reference_steps']!=8192:continue
    s,b=x['strong_l1'],x['weak_payoff_difference']
    rows.append([str(x['n_steps']),f'{s["mean"]:.6f}',f'{b["mean"]:.6f}',f'$[{b["ci95_low"]:.6f},\ {b["ci95_high"]:.6f}]$'])
table('na_results_zh','非仿射模型相对 8192 步参考的结果。100000 条共同路径；区间只量化配对弱差的抽样不确定性。','tab:results-na',['粗步数 $N$','终值强差','有符号收益差','收益差 95\\% 区间'],rows,'rrrr')
rows=[]
for x in na['reference_checks']:
    b=x['weak_payoff_difference']
    rows.append([f'{x["coarser_steps"]}$\\to${x["finer_steps"]}',f'{x["strong_l1"]["mean"]:.8f}',f'{b["mean"]:.8f}',f'$[{b["ci95_low"]:.7f},\ {b["ci95_high"]:.7f}]$'])
table('na_reference_zh','相邻参考网格之间的差。收益差按较粗参考减较细参考计算。','tab:results-reference',['参考步数加密','平均绝对差','收益均值差','收益差 95\\% 区间'],rows,'lrrr')
print('Chinese figures and tables written to',OUT)
