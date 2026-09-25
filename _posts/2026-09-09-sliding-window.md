---
title: "滑动窗口（Sliding Window）"
date: 2026-09-09 21:15:02 +0800
categories: [力扣]
tags: [滑动窗口, Hot100]
description: >-
  维护一个「连续且满足条件」的区间，right 负责扩展、left 负责收缩，两个指针只前进不回退；每个元素最多进一次、出一次，整体 O(n)。
---
## 一句话概括

维护一个「连续且满足条件」的区间，right 负责扩展、left 负责收缩，两个指针只前进不回退；每个元素最多进一次、出一次，整体 O(n)。

## 适用信号

- 题目在说「连续的子数组 / 子串」
- 要求最长、最短或恰好满足某个条件
- 窗口状态可以增量维护（加一个、减一个就够）

## 变长 vs 定长

- 变长窗口：right 扩展，`while` 收缩直到重新合法（第 3 题）
- 定长窗口：长度固定为 m，每步右边进一个、左边出一个，没有 while（第 438 题）

```python
# 变长模板（闭区间 [left, right]）
left = 0
for right in range(n):
    # 1) 扩展：把 s[right] 加入窗口，更新状态
    # 2) 收缩：while 窗口不合法:
    #        移出 s[left]，left += 1
    # 3) 记录：窗口合法时更新答案

# 定长模板（窗口长度固定为 m）
for right in range(n):
    # 1) 把 s[right] 加入窗口
    # 2) if right >= m: 移出 s[right - m]
    # 3) if right >= m - 1: 窗口正好 m 个，判断 / 记录
```

## Python 窗口状态

```python
from collections import Counter

window = Counter()          # 增量维护字符计数
window[s[right]] += 1       # 进窗口
window[s[left]] -= 1        # 出窗口
if window[s[left]] == 0:
    del window[s[left]]     # 归零后删除，保持干净
```

- 异位词 / 字符组成相等的问题，可用长度 26 的计数数组，直接比较两个数组是否相等
- 小写字母计数：`ord(ch) - ord('a')` 得到 0~25 的下标

## Hot 100 两道滑动窗口题

### 3. 无重复字符的最长子串 —— 变长窗口

```python
def length_of_longest_substring(s):
    seen = set()
    left = 0
    best = 0
    for right, ch in enumerate(s):
        while ch in seen:          # 有重复就收缩
            seen.remove(s[left])
            left += 1
        seen.add(ch)
        best = max(best, right - left + 1)
    return best
```

- 窗口始终无重复，长度 = `right - left + 1`（闭区间）
- 易错：收缩必须用 while（可能一次踢多个）；记录发生在窗口合法时
- 进阶：用 dict 存「字符最后出现位置」，left 直接跳到 `last[ch] + 1`，但要判断 `last[ch] >= left` 防止跳到窗口外

### 438. 找到字符串中所有字母异位词 —— 定长窗口

```python
def find_anagrams(s, p):
    n, m = len(s), len(p)
    if n < m:
        return []

    need = [0] * 26
    for ch in p:
        need[ord(ch) - ord('a')] += 1

    window = [0] * 26
    res = []

    for i, ch in enumerate(s):
        window[ord(ch) - ord('a')] += 1            # 右边进
        if i >= m:
            window[ord(s[i - m]) - ord('a')] -= 1  # 左边出
        if i >= m - 1 and window == need:          # 窗口满且计数相等
            res.append(i - m + 1)
    return res
```

- 窗口长度恒为 m，异位词判定 = 字符计数与 need 完全相等
- 易错：窗口未满（`i < m - 1`）时不要比较、不要移出；移出的字符是 `s[i - m]`

## 共同规律

- 3：变长 + 合法条件（窗口内无重复），收缩用 while
- 438：定长 + 精确相等（计数数组相同），固定进一出
- 两题都靠「窗口状态增量更新」避免每段重新统计

## 复杂度

| 题号 | 时间 | 空间 |
| --- | --- | --- |
| 3 | O(n) | O(字符集) |
| 438 | O(n + m)（26 数组比较为常数） | O(1)（不计答案） |
