# 双指数函数曲线拟合工具 / Double-Exponential Curve Fitting

> **Model:** `f(x) = a·exp(b·x) + c·exp(d·x)`

本工具支持：
- 从 Excel Online / Google Sheets / 直链 URL 自动读取数据（第一列 x，第二列 y）
- 通过数学表达式在四个参数 `a, b, c, d` 之间施加等式约束

This tool supports:
- Loading data automatically from an Excel Online / Google Sheets / direct file URL (column 1 = x, column 2 = y)
- Enforcing equality constraints between the four parameters `a, b, c, d` via mathematical expressions

---

## ⚡ PyCharm 快速使用 / PyCharm Quick Start

> 想在 PyCharm 里直接粘贴运行？按下面四步即可，**5 分钟内跑起来**。
>
> Want to paste and run immediately in PyCharm? Follow these four steps.

### 第一步：获取完整代码 / Step 1 – Get the complete code

打开下面的链接，用 **Ctrl+A → Ctrl+C**（Mac: ⌘A → ⌘C）复制全部内容：

Open the link below and press **Ctrl+A → Ctrl+C** (Mac: ⌘A → ⌘C) to copy everything:

👉 **[点击查看/复制完整代码 exponential_fit.py](https://github.com/zhyu-24/test_1/blob/main/exponential_fit.py)**

> 在 GitHub 页面右上角点击 **Raw** 按钮可以看到纯文本代码，更方便全选复制。直接链接：
> [https://raw.githubusercontent.com/zhyu-24/test_1/main/exponential_fit.py](https://raw.githubusercontent.com/zhyu-24/test_1/main/exponential_fit.py)
>
> On the GitHub page click the **Raw** button (top-right) to see plain text — easier to select all. Direct raw link above.

---

### 第二步：在 PyCharm 中新建文件 / Step 2 – Create a new file in PyCharm

1. 打开 PyCharm，新建一个项目（或在已有项目中操作）
2. 在左侧项目面板右键 → **New → Python File**
3. 文件名填 `exponential_fit`（PyCharm 会自动加 `.py`）
4. 将刚才复制的代码全部粘贴进去（**Ctrl+V** / **⌘V**）

Steps:
1. Open PyCharm and create/open a project
2. Right-click the project panel → **New → Python File**
3. Name the file `exponential_fit` (PyCharm adds `.py` automatically)
4. Paste the copied code (**Ctrl+V** / **⌘V**)

---

### 第三步：安装依赖 / Step 3 – Install dependencies

打开 PyCharm 底部的 **Terminal**（终端）标签，运行：

Open the **Terminal** tab at the bottom of PyCharm and run:

```bash
pip install numpy scipy matplotlib requests pandas openpyxl xlrd
```

> 如果提示找不到 `pip`，尝试 `python -m pip install ...`。

---

### 第四步：运行 / Step 4 – Run

在编辑器中右键 → **Run 'exponential_fit'**，或按 **Shift+F10**。

Right-click inside the editor → **Run 'exponential_fit'**, or press **Shift+F10**.

程序会在底部的 **Run** 面板中显示交互式提示。直接按 **Enter** 可跳过 URL 和约束输入，使用内置示例数据。

The program shows interactive prompts in the **Run** panel. Press **Enter** to skip URL / constraint inputs and use the built-in sample data.

---

## 目录 / Contents

1. [环境要求 / Requirements](#环境要求--requirements)
2. [运行方式一：本地 Python（推荐）/ Option 1: Local Python (Recommended)](#运行方式一本地-python推荐--option-1-local-python-recommended)
3. [运行方式二：Google Colab（无需安装，最简单）/ Option 2: Google Colab (Easiest, no install)](#运行方式二google-colab无需安装最简单--option-2-google-colab-easiest-no-install)
4. [运行方式三：Jupyter Notebook / Option 3: Jupyter Notebook](#运行方式三jupyter-notebook--option-3-jupyter-notebook)
5. [运行方式四：在线 IDE（Replit / Gitpod）/ Option 4: Online IDE](#运行方式四在线-idereplit--gitpod--option-4-online-ide)
6. [交互式使用说明 / Interactive Usage Guide](#交互式使用说明--interactive-usage-guide)
7. [在代码中直接调用 / Calling the API Directly](#在代码中直接调用--calling-the-api-directly)
8. [常见问题 / FAQ](#常见问题--faq)

---

## 环境要求 / Requirements

| 依赖 | 最低版本 |
|------|---------|
| Python | 3.8+ |
| numpy | 1.22+ |
| scipy | 1.8+ |
| matplotlib | 3.5+ |
| requests | 2.27+ |
| pandas | 1.4+ |
| openpyxl | 3.0.9+ |
| xlrd | 2.0.1+ |

---

## 运行方式一：本地 Python（推荐）/ Option 1: Local Python (Recommended)

### 第一步：安装 Python / Step 1 – Install Python

如果尚未安装 Python，请前往 [python.org](https://www.python.org/downloads/) 下载并安装 **Python 3.8 或更高版本**。

If Python is not installed, download **Python 3.8+** from [python.org](https://www.python.org/downloads/).

> Windows 用户安装时请勾选 **"Add Python to PATH"**。

---

### 第二步：下载本项目代码 / Step 2 – Get the Code

**方法 A：使用 Git 克隆（推荐）**

```bash
git clone https://github.com/zhyu-24/test_1.git
cd test_1
```

**方法 B：手动下载**

1. 打开 [https://github.com/zhyu-24/test_1](https://github.com/zhyu-24/test_1)
2. 点击绿色 **Code** 按钮 → **Download ZIP**
3. 解压后，用终端/命令提示符进入解压目录

---

### 第三步：安装依赖库 / Step 3 – Install Dependencies

在终端中运行：

```bash
pip install -r requirements.txt
```

> 如果提示权限错误，可以加 `--user` 参数：`pip install --user -r requirements.txt`

---

### 第四步：运行脚本 / Step 4 – Run the Script

```bash
python exponential_fit.py
```

程序启动后会出现交互式提示，见下方[使用说明](#交互式使用说明--interactive-usage-guide)。

The script will start an interactive prompt — see the [usage guide](#交互式使用说明--interactive-usage-guide) below.

---

## 运行方式二：Google Colab（无需安装，最简单）/ Option 2: Google Colab (Easiest, no install)

[Google Colab](https://colab.research.google.com) 是一个**免费**的在线 Jupyter 环境，无需在本机安装任何软件，用 Google 账号即可登录。

[Google Colab](https://colab.research.google.com) is a **free** online Jupyter environment — no local installation required.

**步骤 / Steps:**

1. 打开 [https://colab.research.google.com](https://colab.research.google.com)，用 Google 账号登录
2. 点击菜单 **File → New notebook**（新建笔记本）
3. 在第一个代码格（cell）中粘贴并运行以下命令，安装依赖：

   ```python
   !pip install requests pandas openpyxl xlrd scipy matplotlib
   ```

4. 在第二个代码格中粘贴 `exponential_fit.py` 的全部内容，然后运行
5. 在最后一个代码格中调用：

   ```python
   # 方式一：直接使用示例数据
   from exponential_fit import generate_sample_data, fit_double_exponential, print_results, plot_fit

   x, y, true_params = generate_sample_data()
   popt, pcov, r_sq = fit_double_exponential(x, y)
   print_results(popt, pcov, r_sq, true_params=true_params)
   plot_fit(x, y, popt, r_sq)
   ```

   ```python
   # 方式二：从 URL 读取数据并施加约束
   from exponential_fit import load_data_from_url, fit_double_exponential, print_results, plot_fit

   x, y = load_data_from_url("https://你的Excel链接")
   popt, pcov, r_sq = fit_double_exponential(
       x, y,
       constraint_exprs=["a + c = 1"]   # 根据需要修改
   )
   print_results(popt, pcov, r_sq, constraint_exprs=["a + c = 1"])
   plot_fit(x, y, popt, r_sq, constraint_exprs=["a + c = 1"])
   ```

> **注意：** Colab 中无法使用 `input()` 交互，请直接调用函数（如上方示例）。

---

## 运行方式三：Jupyter Notebook / Option 3: Jupyter Notebook

如果已在本地安装 Jupyter，可以在 notebook 中逐格运行：

If Jupyter is installed locally, you can run the code cell by cell:

```bash
pip install notebook          # 安装 Jupyter（如未安装）
jupyter notebook              # 启动
```

在 notebook 中导入并调用函数的方式与 [Google Colab](#运行方式二google-colab无需安装最简单--option-2-google-colab-easiest-no-install) 相同。

---

## 运行方式四：在线 IDE（Replit / Gitpod）/ Option 4: Online IDE

### Replit（免费）

1. 访问 [https://replit.com](https://replit.com)，注册/登录
2. 点击 **+ Create Repl** → 选择 **Python** → 创建
3. 将 `exponential_fit.py` 和 `requirements.txt` 的内容上传或粘贴进去
4. 在 Shell 中执行：
   ```bash
   pip install -r requirements.txt
   python exponential_fit.py
   ```

---

## 交互式使用说明 / Interactive Usage Guide

运行 `python exponential_fit.py` 后，程序依次询问三个问题：

When you run `python exponential_fit.py`, the program asks three questions in sequence:

---

### 问题 1：数据来源 / Question 1: Data Source

```
[1] Data source / 数据来源
    Paste an Excel Online / Google Sheets / direct file URL,
    or press Enter to use built-in sample data.
    (Column 1 = x axis, Column 2 = y axis)

  URL:
```

- **直接按 Enter**：使用内置示例数据（适合测试）
- **粘贴链接**：支持以下三种格式：

| 来源 | 链接示例 | 要求 |
|------|---------|------|
| **Google Sheets** | `https://docs.google.com/spreadsheets/d/…/edit` | 需设为"任何人均可查看" |
| **OneDrive / Excel Online** | `https://onedrive.live.com/:x:/g/personal/…` 或 `https://…sharepoint.com/…` | 需设为"任何人均可查看" |
| **直链文件** | `https://example.com/data.xlsx` 或 `.csv` | 可直接下载 |

**如何获取 Excel Online 的共享链接？**

1. 在 Excel Online 中打开文件
2. 点击右上角 **共享（Share）** → **复制链接**
3. 确认权限设置为 **"任何人均可查看"**（不需要登录）

---

### 问题 2：参数约束 / Question 2: Parameter Constraints

```
[2] Parameter constraints / 参数约束条件
    Write equality constraints between a, b, c, d.
    ...
  Constraint 1:
```

- **直接按 Enter**：不施加任何约束，进行无约束拟合
- **输入表达式**：每行输入一个约束，输入完毕后按 Enter（空行）结束

**约束表达式示例：**

| 约束含义 | 输入内容 |
|---------|---------|
| a 与 c 之和等于 1 | `a + c = 1` |
| b 等于 d 的 -2 倍 | `b = -2 * d` |
| a·d − b·c = 0 | `a * d - b * c = 0` |
| a 等于 c 的指数 | `a = exp(c)` |

**允许使用的数学函数：** `exp`, `log`, `log2`, `log10`, `sqrt`, `abs`, `sin`, `cos`, `tan`, `pi`, `e`

---

### 问题 3：初始参数猜测 / Question 3: Initial Parameter Guesses

```
[3] Initial parameter guesses / 初始参数猜测 [a, b, c, d]
    Press Enter to use defaults [1.0, -1.0, 1.0, -0.1].

  p0 (four comma-separated numbers):
```

- **直接按 Enter**：使用默认初始值 `[1.0, -1.0, 1.0, -0.1]`
- **输入自定义值**：例如 `3.0, -0.5, 1.5, -0.05`

> 若拟合不收敛，可尝试调整初始值使其更接近预期解。

---

### 输出结果 / Output

拟合完成后，程序将：
1. 在终端打印参数表格（含拟合值、标准误差、R²）
2. 显示拟合曲线图
3. 将图像保存为 `exponential_fit_result.png`

---

## 在代码中直接调用 / Calling the API Directly

```python
import numpy as np
from exponential_fit import (
    load_data_from_url,
    fit_double_exponential,
    print_results,
    plot_fit,
)

# 1. 从 URL 加载数据
x, y = load_data_from_url("https://docs.google.com/spreadsheets/d/YOUR_ID/edit")

# 2. 带约束拟合
constraints = ["a + c = 1", "b = -2 * d"]
popt, pcov, r_sq = fit_double_exponential(
    x, y,
    p0=[2.0, -0.4, -1.0, 0.2],        # 可选：自定义初始值
    constraint_exprs=constraints,
)

# 3. 打印与绘图
print_results(popt, pcov, r_sq, constraint_exprs=constraints)
plot_fit(x, y, popt, r_sq, constraint_exprs=constraints)
```

---

## 常见问题 / FAQ

**Q：运行后提示 `ModuleNotFoundError: No module named 'pandas'`**

A：依赖未安装，请运行：
```bash
pip install -r requirements.txt
```

---

**Q：读取 URL 时提示 `403 Forbidden` 或 `401 Unauthorized`**

A：文件的共享权限不够开放。请确保：
- Google Sheets：共享设置 → **所有知道链接的人**（查看者）
- Excel Online：共享 → **任何人均可查看**（无需登录）

---

**Q：拟合不收敛，提示 `RuntimeError`**

A：尝试更改初始参数猜测值，使其更接近预期的真实值。例如：

```python
popt, pcov, r_sq = fit_double_exponential(x, y, p0=[3.0, -0.5, 1.5, -0.1])
```

---

**Q：施加约束后 R² 比无约束时低，正常吗？**

A：正常。约束缩小了参数的搜索空间，因此当约束与数据存在轻微矛盾时，R² 会略微下降。这是约束拟合的固有权衡。

---

**Q：能否同时施加多个约束？**

A：可以。每行输入一个约束，输入完毕后留空行结束。代码中调用时传入列表即可：

```python
constraint_exprs = ["a + c = 1", "b = -2 * d", "a * d - b * c = 0"]
```
