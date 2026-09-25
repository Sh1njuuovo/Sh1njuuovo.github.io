---
title: "双指针（Two Pointers）"
date: 2026-09-09 12:37:20 +0800
categories: [力扣]
tags: [双指针, Hot100]
description: >-
  用两个下标代替两层循环：每步根据有序性 / 单调性，确定性地移动某一侧指针，跳过大量不可能成立的组合。典型收益：O(n) 时间 + O(1) 额外空间。
---
## 一句话概括

用两个下标代替两层循环：每步根据有序性 / 单调性，确定性地移动某一侧指针，跳过大量不可能成立的组合。典型收益：O(n) 时间 + O(1) 额外空间。

## 适用信号

- 暴力是 O(n²) 的两两配对 / 反复扫描
- 有序数组 + 找一对数 / 找满足条件的区间
- 原地修改数组，要求 O(1) 额外空间
- 回文判断、两端收缩、链表环与中点

## 三种形态

1. **对撞指针**：`left = 0`、`right = n - 1` 相向移动。适合有序配对、水容量类问题。移动依据：谁矮 / 谁小就动谁。
2. **快慢指针**：同向、职责不同。slow 划分「结果区」边界，fast 全场扫描，适合原地过滤、去重。
3. **同向双指针（滑动窗口）**：两个指针都从左往右维护一个区间，Hot 100 里单独归为「滑动窗口」，之后另写笔记。

```python
# 对撞指针模板
left, right = 0, len(arr) - 1
while left < right:
    if 移动左边的依据成立:
        left += 1
    else:
        right -= 1

# 快慢指针模板（原地过滤）
slow = 0
for fast in range(len(arr)):
    if 保留条件(arr[fast]):
        arr[slow] = arr[fast]   # 或交换
        slow += 1
```

## Hot 100 四道双指针题

### 283. 移动零 —— 快慢指针 + 稳定分区

```python
def move_zeroes(nums):
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
```

- slow 左边全是排好的非零，fast 负责扫描
- 易错：交换是核心，保证 0 被换到后面、非零相对顺序不变

### 11. 盛最多水的容器 —— 对撞 + 移动短板

```python
def max_area(height):
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        best = max(best, area)
        if height[left] < height[right]:
            left += 1      # 矮的一侧不可能再成为最优边界
        else:
            right -= 1
    return best
```

- 面积 = min(两端高度) × 宽度；谁矮移谁
- 易错：移动较高的一侧无收益（宽度变小、高度不会变高），可以放心丢弃矮侧

### 15. 三数之和 —— 排序 + 固定 + 对撞 + 去重

```python
def three_sum(nums):
    nums.sort()
    n = len(nums)
    res = []
    for i in range(n - 2):
        if nums[i] > 0:
            break
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        target = -nums[i]
        left, right = i + 1, n - 1
        while left < right:
            cur = nums[left] + nums[right]
            if cur == target:
                res.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif cur < target:
                left += 1
            else:
                right -= 1
    return res
```

- 返回数值而非下标，所以可以放心排序
- 固定一个数后，内层就是「有序数组两数之和」对撞
- 易错：去重三处——外层跳重复固定数、命中后跳重复 left / right

### 42. 接雨水 —— 逐格水量公式 + 对撞省空间

```python
def trap(height):
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1
    return water
```

- 每格水量 = min(左侧最高墙, 右侧最高墙) - 自身高度
- 结算矮侧时，该侧扫过的最高墙已经完整，且它就是 min；另一侧只需兜底，无需知道具体值
- 易错：先想前缀数组版（O(n) 空间）保证理解，再优化成双指针（O(1) 空间）

## 共同规律

暴力慢在 O(n²) 的组合比较 → 双指针让每步移动都有依据、不回退：

- 283：快慢分工，原地稳定分区
- 11：矮侧先定案，丢弃不可能更优的边界
- 15：N 数求和降维成两数求和，排序 + 相邻判断去重
- 42：逐格公式 + 谁矮结算谁，结算侧的最值即 min

## 复杂度

| 题号 | 时间 | 空间 |
| --- | --- | --- |
| 283 | O(n) | O(1) |
| 11 | O(n) | O(1) |
| 15 | O(n²)（含排序 O(n log n)） | O(1)（不计答案） |
| 42 | O(n) | O(1) |
