# Reproducibility check: GBM EM strong slope

## 这项任务是什么意思

这不是要求重新完成整份 coursework，而是抽查一个报告数字能否从对应版本的代码中重现。核验必须同时固定 Git 提交、命令行参数、随机种子、路径数和网格设置。若程序输出四舍五入到三位小数后与报告不同，应以程序结果为准并修改报告。

## 本次选择的数字

报告中的数字是 GBM 实验里 Euler--Maruyama 方法的终值强收敛拟合斜率：

```text
0.500
```

拟合窗口为最细五个网格：`N = 64, 128, 256, 512, 1024`。报告从 `undergraduate_revision/results/report_values.tex` 读取该数值。

## 检出的提交

产生原始实验、代码与结果的提交是：

```text
df9e31f8bba2e8288472630814352ca6698cbd4e
```

在独立 detached worktree 中检出后，`git rev-parse HEAD` 输出：

```text
df9e31f8bba2e8288472630814352ca6698cbd4e
```

## 运行命令

`gbm.py` 记录的默认实验规模为 160,000 条正式路径、20,000 条独立预实验路径和批大小 2,000。本次显式写出这些参数：

```sh
python gbm.py --paths 160000 --pilot-paths 20000 --batch-size 2000
```

程序同时确认随机种子和网格：

```text
seed=2026090804; paths=160000; independent pilot=20000; batch=2000; finest N=1024
```

## 与报告匹配的输出行

```text
"strong_l1_finest_5": 0.4999467662757966,
```

四舍五入到三位小数：

```text
0.4999467662757966 -> 0.500
```

这与报告中的 `0.500` 一致，因此不需要修改报告。

## Ready-to-submit English answer

I checked the reported Euler--Maruyama terminal strong-convergence slope, `0.500`, fitted over `N = 64, 128, 256, 512, 1024`. I checked out commit `df9e31f8bba2e8288472630814352ca6698cbd4e` and ran:

```text
python gbm.py --paths 160000 --pilot-paths 20000 --batch-size 2000
```

The matching output line was:

```text
"strong_l1_finest_5": 0.4999467662757966,
```

This rounds to `0.500` to three decimal places, matching the report. No correction was required.
