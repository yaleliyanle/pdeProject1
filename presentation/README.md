# 金融 SDE 数值方法中文 Beamer 幻灯片

本目录包含面向数值 PDE 初学者的中文课程项目汇报。幻灯片只保留理解数值方法所需的最低金融背景，主线是：

1. 从显式欧拉法过渡到 Euler--Maruyama；
2. 从 Monte Carlo 原理得到标准误和置信区间；
3. 用 GBM 解析解验证 EM 与 Milstein 的强、弱收敛；
4. 用嵌套网格处理无解析解的非仿射模型；
5. 解释为什么现有实验可以支持强半阶，却不足以给出可信弱阶。

## 文件

- `Financial_SDE_Numerical_Methods_Presentation.tex`：Beamer 源文件；
- `Financial_SDE_Numerical_Methods_Presentation.pdf`：已编译的 16:9 幻灯片；
- `Financial_SDE_Numerical_Methods_Presentation_EN.tex`：正式英文 Beamer 源文件；
- `演讲提示.md`：完整版和短版的讲述顺序；
- `assets/`：从项目现有结果中复制的矢量图。
- `assets_en/`：英文演示使用的矢量图。

## 编译

在本目录执行：

```bash
tectonic Financial_SDE_Numerical_Methods_Presentation.tex
```

源文件使用 `ctexbeamer` 与 Noto CJK 字体。提交或演示前，请在标题页把姓名和学号占位线替换为实际信息。

## 建议使用方式

PDF 共 68 页，其中第 63--68 页是备用推导与答疑页。完整教学型汇报约需 45--55 分钟；20--25 分钟汇报可按 `演讲提示.md` 中的短版路线跳页。
