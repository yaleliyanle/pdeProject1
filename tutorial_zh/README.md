# 第四题中文学习讲义

先打开 **Problem4_Chinese_Tutorial.pdf**。讲义共 45 页，面向只有概率论基础、没有随机微积分或随机微分方程基础的读者。

内容依次包括题意拆解、随机过程与布朗运动、条件期望与鞅、Itô 积分和二次变差、Itô 公式、GBM 精确解、EM 与 Milstein 推导、强弱误差及置信区间、非仿射波动率模型、数值参考的局限、五个控制变量的推导、现有 Python 代码解释、原数值结果解读和练习答案。

## 文件

- `Problem4_Chinese_Tutorial.pdf`：已编译的中文讲义。
- `Problem4_Chinese_Tutorial.tex`：完整可编辑 TeX；章节和表格已合并，编译不依赖 `drafts/`。
- `assets/`：主 TeX 使用的图文件；另含由原数据生成的表格片段。
- `teaching_demo.py`：仅 NumPy 依赖的教学示例，默认 2000 条路径，只打印结果。
- `audit_saved_results.py`：读取上一级原项目保存数据，独立复核可恢复的统计量。
- `validation_saved.json`：保存数据复核结果，PASS，并列出检查范围和局限。
- `build_assets.py`：读取上一级原项目 CSV/JSON，重绘中文图表，需要 NumPy 和 Matplotlib。
- `drafts/`、`assemble_tex.py`：制作时的章节片段及组装程序。若直接修改主 TeX，请勿再运行组装程序覆盖改动。
- `build/`：编译日志、教学脚本输出、页面渲染与排版检查记录。

原题副本与用户下载目录中的 PDF 经 SHA-256 检查一致。原有 Python 代码、英文报告和 `results/` 数据没有修改。

## 阅读与运行

在原项目根目录运行：

```sh
python3 tutorial_zh/teaching_demo.py --self-check
python3 tutorial_zh/teaching_demo.py
python3 tutorial_zh/teaching_demo.py --paths 8000 --seed 12345
python3 tutorial_zh/audit_saved_results.py
```

教学脚本的自检检查布朗粗化、GBM 递推、旧状态同步更新、常波动率退化、稳定 logistic 和标准误差计算。其默认运行也已通过。小规模示例帮助理解实现，不保证重现原大样本的收敛斜率，不覆盖原结果。

原代码的 `verify.py` 需要 Numba，并会写入原 `results/verification.json`；本次没有直接运行这个原脚本，也没有重跑全部大型实验。新增核验脚本使用 NumPy 独立检查终值数组与统计表。

## 编译

在 `tutorial_zh/` 内运行：

```sh
tectonic --keep-logs Problem4_Chinese_Tutorial.tex
```

或者在安装完整 TeX 发行版后运行两次：

```sh
xelatex -interaction=nonstopmode -halt-on-error Problem4_Chinese_Tutorial.tex
xelatex -interaction=nonstopmode -halt-on-error Problem4_Chinese_Tutorial.tex
```

需要 `ctexart` 等导言区列出的宏包，以及 Noto Serif CJK SC、Noto Sans CJK SC、Noto Sans Mono CJK SC 字体。若机器上字体不同，修改导言区的字体配置。Tectonic 首次运行可能下载所需 TeX 宏包；本次最终编译已使用缓存完成。

已检查：45 页 PDF 可打开；没有未定义引用、缺失字符或版面溢出；已目视抽查封面、理论、代码与图表页面。编译器关于使用本机绝对字体路径的环境提示不影响 PDF 阅读；在其他机器重新编译需安装字体或调整配置。

压缩包包含阅读与重新编译讲义所需的 PDF、TeX 和图文件，并附教学脚本。数据核验、图表再生成依赖原项目的 `results/`、`figures/`，请保留这里作为原项目子目录的布局。
