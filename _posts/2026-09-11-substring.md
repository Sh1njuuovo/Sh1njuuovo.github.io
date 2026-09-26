---
title: "子串（Substring / Subarray）"
date: 2026-09-11 13:03:01 +0800
categories: [算法]
tags: ["LeetCode Hot 100"]
description: >-
  子串问题的共性是「连续」。暴力枚举所有区间的成本是 O(n²)，优化的方向都是让区间信息可增量维护，具体按问题类型选三种工具。
---
## 一句话概括

子串问题的共性是「连续」。暴力枚举所有区间的成本是 O(n²)，优化的方向都是让区间信息可增量维护，具体按问题类型选三种工具。

## 怎么选工具

- 问「多少个子数组 / 存在不存在某个和」→ 前缀和 + 哈希
- 问「最短 / 最长满足条件的连续区间」→ 滑动窗口（见 sliding-window.md）
- 问「固定窗口内的最大 / 最小」→ 单调队列

## 工具一：前缀和 + 哈希

```python
def subarray_sum(nums, k):
    count = {0: 1}     # 前缀和 -> 出现次数
    pre = 0
    res = 0
    for x in nums:
        pre += x
        res += count.get(pre - k, 0)   # 先查
        count[pre] = count.get(pre, 0) + 1   # 后存
    return res
```

下标约定（重要，别混）：

- `P[j]` = 前 j 个元素之和，`P[0] = 0`，数组长度 n+1
- 子数组 `nums[t..i]` 的和 = `P[i+1] - P[t]`，左端点 t 对应 `P[t]`
- 循环里的滚动变量 `pre` 产生的是 `P[1]..P[n]`，`P[0]` 由 `{0: 1}` 登记
- 若改用 `Q[k] = nums[0] + ... + nums[k]` 的约定，公式才会变成 `Q[i] - Q[t-1]`

## 工具二：滑动窗口

变长用 while 收缩，定长固定进一出，细节见 sliding-window.md。子串问题里额外常用的是**需求计数 + 满足计数**：need 记录目标字符计数，have 记录已达标的字符种类数，用 `have == len(need)` 做 O(1) 合法性判断。

## 工具三：单调队列

```python
from collections import deque

def max_sliding_window(nums, k):
    dq = deque()      # 存下标，值从队首到队尾递减
    res = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()             # 又旧又小的元素永远没机会了
        dq.append(i)
        if dq[0] <= i - k:       # 队首过期
            dq.popleft()
        if i >= k - 1:
            res.append(nums[dq[0]])
    return res
```

- 队列存**下标**，因为要判断是否滑出窗口
- 每个下标进出队各一次，摊销 O(n)

## Hot 100 三道子串题

### 560. 和为 K 的子数组 —— 前缀和 + 哈希

```python
def subarray_sum(nums, k):
    count = {0: 1}
    pre = 0
    res = 0
    for x in nums:
        pre += x
        res += count.get(pre - k, 0)
        count[pre] = count.get(pre, 0) + 1
    return res
```

- 子数组和 = 两个前缀和之差，问题变成「历史里有多少个 pre - k」
- 易错：`{0: 1}` 不能省（漏掉从头开始的子数组）；必须**先查后存**，否则 k = 0 时会数出长度为 0 的空子数组
- 有负数时不能用滑动窗口，只能用前缀和

### 239. 滑动窗口最大值 —— 单调队列

```python
from collections import deque

def max_sliding_window(nums, k):
    dq = deque()
    res = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            res.append(nums[dq[0]])
    return res
```

- 核心是支配关系：新元素更大更靠右，队尾那些小的旧元素永远当不上最大值
- 易错：步骤顺序固定为「清队尾 → 入队 → 查队首过期 → 记录」；前 k-1 轮窗口没满，不要记录

### 76. 最小覆盖子串 —— 变长窗口 + 需求计数

```python
from collections import Counter

def min_window(s, t):
    if not t or not s:
        return ""
    need = Counter(t)
    window = {}
    have = 0
    required = len(need)
    left = 0
    best_len = float('inf')
    best_left = 0

    for right, ch in enumerate(s):
        window[ch] = window.get(ch, 0) + 1
        if window[ch] == need[ch]:
            have += 1

        while have == required:
            if right - left + 1 < best_len:
                best_len = right - left + 1
                best_left = left
            left_ch = s[left]
            window[left_ch] -= 1
            if window[left_ch] < need[left_ch]:
                have -= 1
            left += 1

    return "" if best_len == float('inf') else s[best_left:best_left + best_len]
```

- `have` 记录已达标的字符**种类数**，合法条件是 `have == len(need)`
- 易错：`required` 用 `len(need)` 而不是 `len(t)`（t 有重复字符时种类数更少）；加字符刚好达标才 `have += 1`，减字符掉到需求以下才 `have -= 1`；答案在 while 里更新，且要同时记录起点和长度
- 备注：`need` 是 Counter 时，读缺失 key 返回 0，`in need` 判断可以省；换普通 dict 就必须加

## 三道题对比

| 题号 | 问什么 | 工具 | 时间 | 空间 |
| --- | --- | --- | --- | --- |
| 560 | 多少个和为 k 的子数组 | 前缀和 + 哈希 | O(n) | O(n) |
| 239 | 每个窗口内的最大值 | 单调队列 | O(n) | O(k) |
| 76 | 最短覆盖 t 的子串 | 滑动窗口 + 需求计数 | O(n + m) | O(字符集) |
