---
title: "回溯（Backtracking）"
date: 2026-09-22 21:58:27 +0800
categories: [算法]
tags: ["LeetCode Hot 100"]
description: >-
  回溯就是系统地穷举所有可能的解。代码形状是深度优先搜索，区别在于每走一步都要能退回来。整套模板的核心只有三行，做选择、递归、撤销选择。
---
## 一句话概括

回溯就是系统地穷举所有可能的解。代码形状是深度优先搜索，区别在于每走一步都要能退回来。整套模板的核心只有三行，做选择、递归、撤销选择。

## 核心框架

```python
def backtrack(路径, 选择列表):
    if 满足结束条件:
        记录结果
        return

    for 选择 in 选择列表:
        if 选择不合法:
            continue
        做选择
        backtrack(新的路径, 新的选择列表)
        撤销选择
```

三行的顺序永远固定。加了不撤，路径会污染后面的分支。

## 怎么选模板

拿到一道题，先回答三个问题。

- 路径是什么，也就是已经做出的选择
- 每一层有哪些选择
- 什么时候算走完

然后看结果里元素有没有顺序，选两种模板之一。

| | 组合、子集型 | 排列型 |
| --- | --- | --- |
| 元素有先后区别吗 | 没有，[1,2] 和 [2,1] 算同一个 | 有，[1,2] 和 [2,1] 是两个答案 |
| 靠什么防重复 | start 参数，只能往后挑 | used 数组，跳过已用的 |
| 递归传什么 | i + 1，写 i 表示允许重复用 | 不需要 start，循环整个数组 |
| 记录答案的时机 | 看题目，常见是每个节点都记 | 只有叶子节点 |
| 代表题 | 78 子集、39 组合总和、131 分割回文串 | 46 全排列 |

## Python 基础

### 为什么必须复制 path

```python
res.append(path)        # 错，所有答案会指向同一个列表
res.append(path[:])     # 对，复制一份
```

`path` 从头到尾是同一个对象。函数返回时它已经被弹空了，不复制的话最后 `res` 里全是空列表。

### 为什么必须撤销

`path.append(x)` 和 `path.pop()` 要成对出现。不撤销的话，上一层做的选择会带进下一个分支，路径越来越长，答案全错。

用 `used` 数组的时候，`used[i] = True` 和 `used[i] = False` 也要成对。这题改的是共享状态，比单独的 path 更容易漏。

### 剪枝的两类

第一类为了减少搜索。不剪枝答案也对，只是慢。比如 39 组合总和，和超过目标就停。

第二类为了保证生成的都是合法解。不剪枝会生成非法结果，还得最后再过滤一遍。比如 22 括号生成的前缀检查，131 分割回文串的非回文跳过。

### 用 break 还是 continue

判断标准是，后面的选项能不能从当前这个选项推出结论。

- 能推出来，用 break。39 里数组排好序了，当前这个数太大，后面的更大
- 推不出来，用 continue。131 里字符串没有顺序，`ab` 不是回文不代表 `aba` 不是

### 复杂度怎么看

回溯的复杂度都是指数级或者阶乘级，看的是结果的数量和每个结果的长度。

- 子集有 2 的 n 次方个结果，每个结果最长 n，所以是 O(n × 2ⁿ)
- 全排列有 n 的阶乘个结果，所以是 O(n × n!)
- 括号生成的结果数是卡特兰数

面试里说出「有多少个结果，每个结果多长」比背公式更管用。

## Hot 100 八道题

### 46. 全排列 —— 排列型

```python
def permute(nums):
    res = []
    path = []
    used = [False] * len(nums)

    def backtrack():
        if len(path) == len(nums):      # 选满了，是一个完整排列
            res.append(path[:])
            return

        for i in range(len(nums)):
            if used[i]:                 # 这个数已经在路径上了
                continue
            used[i] = True              # 做选择
            path.append(nums[i])
            backtrack()                 # 进入下一层
            path.pop()                  # 撤销选择
            used[i] = False             # 标记也要撤销

    backtrack()
    return res
```

- 每层循环整个数组，跳过 `used` 为真的下标
- 排列里顺序有区别，所以每层都能从整个数组挑，只排除路径上已经有的
- 结束条件是路径长度等于数组长度，只有叶子节点才是答案
- 易错：忘了 `used[i] = False`，代码不报错但答案会少
- 易错：`res.append(path)` 而不是 `path[:]`

### 78. 子集 —— 组合型

```python
def subsets(nums):
    res = []
    path = []

    def backtrack(start):
        res.append(path[:])             # 每个节点都是答案
        for i in range(start, len(nums)):
            path.append(nums[i])        # 做选择
            backtrack(i + 1)            # 只能往右边挑
            path.pop()                  # 撤销选择

    backtrack(0)
    return res
```

- 记录答案写在函数开头、循环之前，因为每个节点都是一个合法子集
- 不需要写结束条件，`start` 走到末尾时循环自然为空
- `backtrack(i + 1)` 保证下一层只能往右挑，不会出现 `[2, 1]` 这种和 `[1, 2]` 重复的结果
- 易错：`backtrack(i)` 会无限递归，同一个数一直加
- 易错：记录答案写在循环里，会漏掉空集

### 17. 电话号码的字母组合 —— 选择列表来自映射表

```python
def letterCombinations(digits):
    if not digits:                      # 空字符串要单独处理
        return []

    phone = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
    }

    res = []
    path = []

    def backtrack(index):
        if index == len(digits):
            res.append("".join(path))
            return
        for ch in phone[digits[index]]:     # 这一层的选择列表
            path.append(ch)
            backtrack(index + 1)
            path.pop()

    backtrack(0)
    return res
```

- 每个数字一组字母，各组的字母互不重叠，所以既不需要 start 也不需要 used
- `index` 表示处理到第几个数字，同时充当结束判断
- 结果用 `"".join(path)` 拼成字符串，因为 join 会生成新对象，不用再复制 path
- 易错：忘了开头那句 `if not digits: return []`，输入空串会得到 `[""]` 而不是 `[]`
- 易错：映射表里 7 和 9 是四个字母，其余是三个

### 39. 组合总和 —— 可重复选择加剪枝

```python
def combinationSum(candidates, target):
    candidates.sort()                   # 排序是剪枝的前提
    res = []
    path = []

    def backtrack(start, cur_sum):
        if cur_sum == target:
            res.append(path[:])
            return

        for i in range(start, len(candidates)):
            if cur_sum + candidates[i] > target:
                break                   # 后面的数更大，整个循环都可以退
            path.append(candidates[i])
            backtrack(i, cur_sum + candidates[i])    # 传 i，可以重复用
            path.pop()

    backtrack(0, 0)
    return res
```

- 传 `i` 而不是 `i + 1`，允许同一个数被重复选
- 传 `i` 而不是 `0`，保证选出来的序列非递减，这样同一个组合只会生成一次
- `break` 成立的前提是数组已经排好序
- 剪枝条件必须是 `> target`，写成 `>=` 会把正好等于目标的那一步砍掉
- 易错：忘了排序，`break` 会错杀正确答案

### 22. 括号生成 —— 合法性剪枝

```python
def generateParenthesis(n):
    res = []
    path = []

    def backtrack(left, right):
        if len(path) == 2 * n:              # 括号用完了
            res.append("".join(path))
            return

        if left < n:                        # 左括号还有额度
            path.append("(")
            backtrack(left + 1, right)
            path.pop()

        if right < left:                    # 右括号不能超过左括号
            path.append(")")
            backtrack(left, right + 1)
            path.pop()

    backtrack(0, 0)
    return res
```

- 这题没有 for 循环。选择只有两个，长度固定，直接写两条 if 比写循环清楚
- 两条规则保证了任何前缀都合法，所以走到末尾的一定是合法串，不需要最后再检查
- 右括号的条件是严格小于，写成 `right <= left` 会生成 `())(` 这种非法串
- 两个 if 不能合成 if else，有些时刻两个条件同时成立
- 结果数是卡特兰数，n 等于 8 时是 1430 个

### 79. 单词搜索 —— 网格上的回溯

```python
def exist(board, word):
    m, n = len(board), len(board[0])
    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def dfs(i, j, k):
        if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[k]:
            return False
        if k == len(word) - 1:          # 最后一个字符也匹配上了
            return True

        board[i][j] = "#"               # 做选择，标记这个格子已用
        found = False
        for di, dj in dirs:
            if dfs(i + di, j + dj, k + 1):
                found = True
                break
        board[i][j] = word[k]           # 撤销选择，成功失败都要恢复

        return found

    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):            # 每个格子都当一次起点
                return True
    return False
```

- 和前面几题不同，这题是找一个解就停，`dfs` 要有返回值
- 三层结构，外层枚举起点，中层是 dfs，内层是四个方向
- 越界判断写在 `or` 的最前面，靠短路避免下标越界
- 用 `#` 覆盖棋盘当作 visited，回溯时恢复。忘了恢复的话后面的起点就搜不到了
- 用 `found` 变量是为了保证无论走通还是走不通，恢复那一行都会执行
- 复杂度 O(m × n × 3 的 L 次方)，因为每一步有一个方向是来路，只剩 3 个分支

### 131. 分割回文串 —— 字符串切分

```python
def partition(s):
    res = []
    path = []

    def backtrack(start):
        if start == len(s):                     # 切到末尾了
            res.append(path[:])
            return

        for end in range(start, len(s)):
            sub = s[start:end + 1]              # 切片右端要加一
            if sub != sub[::-1]:                # 不是回文就跳过
                continue
            path.append(sub)
            backtrack(end + 1)                  # 从这一段的右边继续
            path.pop()

    backtrack(0)
    return res
```

- 结构上和 78 子集几乎一样，只是把「挑一个数」换成「挑一个结尾位置」
- `start` 表示从现在的位置开始切，`end` 是这一段的结尾
- 切片必须写 `s[start:end + 1]`，Python 的切片右端不含
- 不是回文要用 `continue`。用 `break` 的话，`abac` 里 `ab` 不是回文就会把 `aba` 这一支也砍掉
- 递归要传 `end + 1`，传 `end` 会无限递归

### 51. N 皇后 —— 棋盘约束

```python
def solveNQueens(n):
    res = []
    cols = set()          # 已占用的列
    diag1 = set()         # 已占用的左上到右下的斜线，存 row - col
    diag2 = set()         # 已占用的右上到左下的斜线，存 row + col
    queens = []           # queens[row] 是这一行皇后所在的列

    def backtrack(row):
        if row == n:
            board = []
            for c in queens:
                board.append("." * c + "Q" + "." * (n - c - 1))
            res.append(board)
            return

        for c in range(n):
            if c in cols or (row - c) in diag1 or (row + c) in diag2:
                continue                    # 这个位置放不了

            cols.add(c)                     # 做选择
            diag1.add(row - c)
            diag2.add(row + c)
            queens.append(c)

            backtrack(row + 1)              # 进入下一行

            queens.pop()                    # 撤销选择，四个都要还原
            cols.remove(c)
            diag1.remove(row - c)
            diag2.remove(row + c)

    backtrack(0)
    return res
```

- 每行必须放且只放一个皇后，所以用行号当递归层数，同行的冲突自动消失
- 左上到右下的斜线用 `row - col` 表示，往右下走两个一起加，差不变
- 右上到左下的斜线用 `row + col` 表示，往左下走行加列减，和不变
- 用三个集合把二维的斜线压成一维的数，冲突判断做到 O(1)
- 撤销时有四个动作，`queens` 和三个集合都要还原
- 边界：n 等于 2 和 3 无解，返回空列表

## 八题总表

| 题号 | 每层的选择 | 结束条件 | 剪枝方式 | 时间 |
| --- | --- | --- | --- | --- |
| 46 全排列 | 从没用过的数里挑一个 | 长度等于 n | 无 | O(n × n!) |
| 78 子集 | 从 start 往后挑一个 | 循环自然结束 | 无 | O(n × 2ⁿ) |
| 17 电话号码 | 当前数字的字母里挑一个 | 处理完所有数字 | 无 | O(n × 4ⁿ) |
| 39 组合总和 | 从 start 往后挑，可重复 | 和等于目标 | 超了 break | 指数级 |
| 22 括号生成 | 加左括号或者加右括号 | 用满 n 对 | 前缀不合法就走不了 | 卡特兰数 |
| 79 单词搜索 | 往四个方向走一步 | 匹配完整个单词 | 越界或者字母不对 | O(mn × 3^L) |
| 131 分割回文串 | 挑下一段的结尾位置 | 切到字符串末尾 | 不是回文 continue | O(n × 2ⁿ) |
| 51 N 皇后 | 这一行的皇后放哪一列 | 放满 n 行 | 列和对角线冲突就跳过 | O(n!) |

`n` 是数组或者字符串长度，`L` 是单词长度，`m` 和 `n` 在 79 那一行指网格的长宽。

## 共同规律

第一，八道题都是同一个模板。变化的只有三件事，选择列表是什么，什么时候记录答案，什么情况该剪枝。

| 题号 | 选择列表来自哪里 | 记录答案的位置 |
| --- | --- | --- |
| 78、39、131 | 同一个数组或字符串上的一段 | 每个节点，或者满足条件时 |
| 46 | 整个数组，排除已用的 | 只有叶子节点 |
| 17 | 每个数字对应的字母表 | 只有叶子节点 |
| 22 | 固定的两个动作 | 只有叶子节点 |
| 79 | 网格上四个方向的邻居 | 匹配完成时立刻返回 |
| 51 | 当前行的 n 个列 | 放满 n 行时 |

第二，防重复的方式由定位参数决定。组合类用 `start`，排列类用 `used`，切分类用 `end` 之后的下一个位置。想清楚「下一层能从哪里开始」，重复问题自然就解决了。

第三，剪枝条件来自一句话，什么样的前缀不可能再补成答案。39 的前缀是「和已经超过目标」，22 的前缀是「右括号已经比左括号多」，131 的前缀是「这一段不是回文」，51 的前缀是「这个格子和已有的皇后冲突」。

第四，分清「枚举所有解」和「找到一个解就停」。前者不需要返回值，往 `res` 里追加。后者要让递归函数返回 True 或者 False，找到了就一路往上传。

第五，记录答案的位置由决策树的形状决定。78 的每个节点都是答案，46 只有叶子是答案，79 是中途匹配到就算成功。写之前先画出决策树，看清楚答案在哪一层。

