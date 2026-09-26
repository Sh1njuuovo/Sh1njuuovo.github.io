---
title: "二分查找（Binary Search）"
date: 2026-09-23 13:19:00 +0800
categories: [算法]
tags: [刷题]
description: >-
  二分查找在有序区间里每次丢掉一半，把 O(n) 的线性扫描压到 O(log n)。核心动作只有一个，每轮看中间那个值，根据它和目标的大小关系，判断答案在左半边还是右半边，然后把这个范围缩掉一半。
---
## 一句话概括

二分查找在有序区间里每次丢掉一半，把 O(n) 的线性扫描压到 O(log n)。核心动作只有一个，每轮看中间那个值，根据它和目标的大小关系，判断答案在左半边还是右半边，然后把这个范围缩掉一半。

## 什么时候用它

- 数组有序，或者题目给的数据有单调性，要找某个值或者它的位置
- 题目里出现「有序」「排序」「旋转」这些词，要找边界、找最小值、找插入点
- 二维矩阵如果整体递增，也能当成一维有序数组处理
- 求「最小的最大值」这类带单调性的答案，用二分答案

反过来说，如果数据没有单调性，二分挑错了方向，答案直接就是错的。这是用二分之前要先确认的一件事。

## Python 基础

### 区间的两种写法

二分最容易乱的地方是区间怎么定义。只有两种主流写法，选一种用到底，别混。

| | 闭区间 `[left, right]` | 左闭右开 `[left, right)` |
| --- | --- | --- |
| right 的初值 | `len(nums) - 1` | `len(nums)` |
| 循环条件 | `left <= right` | `left < right` |
| 更新 right | `right = mid - 1` | `right = mid` |
| 更新 left | `left = mid + 1` | `left = mid + 1` |
| 循环结束时 | 没找到返回 -1 | `left` 是第一个不小于目标的位置 |

闭区间的循环条件带等号，因为区间里只剩一个元素时也要检查它。右开区间里 `right` 本身不取，所以循环条件不带等号，缩边界时 `right = mid` 就够，不用减一。

### mid 的两种写法

```python
mid = left + (right - left) // 2      # 推荐
mid = (left + right) // 2             # 结果一样，但别的语言会溢出
```

Python 的整数不会溢出，两种写法结果完全相同。推荐第一种是因为它把计算范围限制在 `left` 到 `right` 之间，以后写 C++ 或者 Java 时不会踩整型溢出的坑。另外这种写法在区间长度为偶数时取的是偏左的中点。

### 循环不变量

写二分之前先在心里定一句话，比如「答案一定在当前区间里」。之后每一步操作都要保证这句话还成立。区间缩到空或者只剩一个位置的时候，剩下的那个地方就是答案。这么想边界就不会写错。

## 四种模板

模板一，找准确的目标值，闭区间写法。

```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

模板二，lower_bound，找第一个大于等于目标的位置，左闭右开写法。

```python
def lower_bound(nums, target):
    left, right = 0, len(nums)
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
```

它的返回值和三条性质。

- 返回的 `left` 就是第一个大于等于 target 的下标
- 如果所有元素都小于 target，返回 `len(nums)`
- 如果 `left < len(nums)` 并且 `nums[left] == target`，说明找到了

35、34 两题都建立在这个模板上，这是本组最值得背下来的一段。

模板三，二分答案。当答案本身有单调性时，不去数组里找值，而是猜一个答案，写一个检查函数判断它行不行。

```python
left, right = 下界, 上界
while left < right:
    mid = left + (right - left) // 2
    if check(mid):          # mid 可行，试着再小一点
        right = mid
    else:                   # mid 不可行，必须变大
        left = mid + 1
return left
```

`check(x)` 返回「答案为 x 时能不能满足题目的要求」。因为答案越小时越难满足，这个真假变化只有一个转折点，正好可以用二分找到那个转折点。Hot 100 里没有纯二分答案的题，面试里常见，知道思路就行。

## 怎么判断用哪个

- 有序数组里找一个确定的值，找到返回下标，找不到返回 -1，用模板一
- 找第一个满足条件的位置，比如插入位置、左边界，用模板二
- 找一段连续区间的第一个和最后一个位置，调用两次模板二
- 数组被旋转过，先判断哪一半有序，再去有序的那一半里找
- 两个有序数组求中位数，二分短数组上的一刀切在哪里
- 答案本身单调，求最小的最大值或者最大的最小值，用二分答案

## Hot 100 六道题

### 35. 搜索插入位置

```python
def searchInsert(nums, target):
    left, right = 0, len(nums)
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
```

- 这题就是 lower_bound 本身，找第一个大于等于 target 的位置
- 用左闭右开，`right` 从 `len(nums)` 开始，循环条件是 `left < right`
- 为什么返回 `left` 就对。区间缩到空的时候，`left` 正好落在第一个不小于目标的位置上，插入到它前面就能保持有序
- target 比所有数都大时返回 `len(nums)`，正好是插到末尾
- 易错：`right` 写成 `len(nums) - 1` 或者循环条件写成 `left <= right`，这两个必须配套，改一个忘一个就会错

### 74. 搜索二维矩阵

```python
def searchMatrix(matrix, target):
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1
    while left <= right:
        mid = left + (right - left) // 2
        row, col = mid // n, mid % n
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] < target:
            left = mid + 1
        else:
            right = mid - 1
    return False
```

- 题目的条件有两层，每行递增，并且每行的第一个数大于上一行的最后一个数。合起来整个矩阵从上到下、从左到右就是一个有序的一维数组
- 把一维下标 `mid` 换算成行列，`mid // n` 是行号，`mid % n` 是列号，这一步是本题的关键
- 换算之后就是标准的闭区间二分
- 易错：`//` 和 `%` 用反，行列会串位；忘记先判断矩阵为空
- 注意区分。如果矩阵只是每行每列各自递增，并不保证整体有序，那就得用 240 题的右上角收缩法，不能这样二分

### 34. 在排序数组中查找元素的第一个和最后一个位置

```python
def searchRange(nums, target):
    def lower(x):
        left, right = 0, len(nums)
        while left < right:
            mid = left + (right - left) // 2
            if nums[mid] < x:
                left = mid + 1
            else:
                right = mid
        return left

    start = lower(target)
    if start == len(nums) or nums[start] != target:
        return [-1, -1]
    end = lower(target + 1) - 1        # 第一个大于 target 的位置再减一
    return [start, end]
```

- 同一套 `lower` 调两次解决，不用手写四种边界判断
- 左边界就是第一个大于等于 target 的位置
- 右边界换个思路求。`lower(target + 1)` 是第一个大于等于 target + 1 的位置，对于整数来说就是第一个大于 target 的位置，它减一正好落在最后一个 target 上
- 两个易错点。第一，算之前要先确认 target 在不在数组里，否则 `start` 可能等于 `len(nums)` 或者指向别的数，下面就会错。第二，算右边界时用的是 `target + 1` 这个技巧，不需要再写第二个函数
- Python 里也有现成的 `bisect_left` 和 `bisect_right`，`bisect_left` 就是 `lower`，用 `bisect_right` 减一也能拿到右边界。考试或者面试里手写更稳，也更能说明思路

### 33. 搜索旋转排序数组

```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:            # 左半段有序
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:                                  # 右半段有序
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

- 数组被旋转过，整体不有序，但是任意时刻从 `mid` 切开，一定有一半是有序的
- 先判断哪一半有序，再看 target 在不在这一半的值范围内。在就进去找，不在就跳到另一半
- `nums[left] <= nums[mid]` 里的 `<=` 不能写成 `<`，这是本题最隐蔽的地方。最小反例是 `[2, 1]` 里找 1
  - 此时 `left = 0`，`mid = 0`，`nums[left]` 和 `nums[mid]` 是同一个数，都是 2
  - 用 `<=`，判定左半段有序，接着 `nums[left] <= target < nums[mid]` 就是 `2 <= 1 < 2`，不成立，于是 `left = mid + 1 = 1`，下一轮找到 1
  - 用 `<`，判定左半段无序，跳到右边的分支，`nums[mid] < target <= nums[right]` 是 `2 < 1 <= 1`，不成立，于是 `right = mid - 1 = -1`。区间直接缩没了，返回 -1，答案丢了
  - 根本原因是 `left` 和 `mid` 相等时，左半段只有一个元素，它当然是有序的，`<=` 才是正确的判断
- 另一处易错是范围判断两边都要带边界，写成 `nums[left] <= target < nums[mid]`，少一个符号答案就会错

### 153. 寻找旋转数组中的最小值

```python
def findMin(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            left = mid + 1        # 最小值在右半段
        else:
            right = mid           # 最小值在左半段，mid 自己也可能是最小值
    return nums[left]
```

- 和 33 的区别在于，这题不找具体某个值，而是找最小值所在的位置，所以拿 `nums[mid]` 和 `nums[right]` 比
- 为什么不和左端比。因为整体不旋转时数组完全有序，和右端比能一路把区间收到最左边，和左端比就会把最小值丢掉
- `nums[mid] > nums[right]` 说明 mid 落在左边那段升序里，最小值一定在 mid 的右边，所以 `left = mid + 1`
- 否则最小值就在 mid 或者它左边，因为 mid 自己也可能是最小值，所以是 `right = mid`，不能减一
- 循环条件是 `left < right`。循环结束时 `left == right`，直接返回 `nums[left]`
- 易错：循环条件写成 `left <= right` 会死循环；`right = mid` 写成 `right = mid - 1` 会把最小值跳过去

### 4. 寻找两个正序数组的中位数

```python
def findMedianSortedArrays(nums1, nums2):
    if len(nums1) > len(nums2):        # 保证 nums1 是短的那个
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    total_left = (m + n + 1) // 2      # 左半部分一共要有多少个元素

    left, right = 0, m
    while left <= right:
        i = left + (right - left) // 2     # nums1 切在 i，左边取 i 个
        j = total_left - i                 # nums2 左边取 j 个，凑够总数

        left1 = nums1[i - 1] if i > 0 else float("-inf")
        right1 = nums1[i] if i < m else float("inf")
        left2 = nums2[j - 1] if j > 0 else float("-inf")
        right2 = nums2[j] if j < n else float("inf")

        if left1 <= right2 and left2 <= right1:
            if (m + n) % 2 == 1:
                return max(left1, left2)
            return (max(left1, left2) + min(right1, right2)) / 2
        elif left1 > right2:              # nums1 左边取多了
            right = i - 1
        else:                             # nums1 左边取少了
            left = i + 1
```

- 目标是把两个数组合并后的左半部分和右半部分切开。左半部分一共有 `total_left = (m + n + 1) // 2` 个元素。加一是为了让奇数长度时左半部分多一个，中位数直接就是左半部分的最大值
- 只在短数组上做二分。在 nums1 上切一刀 i，nums2 上的刀口 j 由 `total_left - i` 定死，不用再猜
- 正确的切分同时满足两个条件，`left1 <= right2` 并且 `left2 <= right1`。四个变量是左半部分的最大值和右半部分的最小值，越界的部分用正负无穷补上，省掉一堆 if
- 调整的方向。`left1 > right2` 说明 nums1 左边取多了，右界左移。否则说明取少了，左界右移
- 拿到正确的切分以后，奇数长度返回 `max(left1, left2)`，偶数长度返回左边最大和右边最小的平均值
- 复杂度是 O(log(min(m, n)))，只和短数组的长度有关
- 易错：开头忘记交换，nums1 不是短数组，后面 i 的范围会越界；`total_left` 忘记加一；越界时没有用正负无穷兜底

## 六题总表

| 题号 | 题目特征 | 用的模板 | 关键点 | 时间 |
| --- | --- | --- | --- | --- |
| 35 搜索插入位置 | 有序数组，找插入点 | lower_bound，左闭右开 | 最后返回 left | O(log n) |
| 74 搜索二维矩阵 | 整体有序的二维数组 | 闭区间二分 | `mid // n` 和 `mid % n` | O(log(mn)) |
| 34 找首末位置 | 有序数组，找左右边界 | 两次 lower_bound | `lower(target + 1) - 1` | O(log n) |
| 33 搜索旋转数组 | 旋转过的有序数组 | 闭区间二分加有序性判断 | `nums[left] <= nums[mid]` | O(log n) |
| 153 找最小值 | 旋转过的有序数组 | 和右端比较 | 往左缩时写 `right = mid` | O(log n) |
| 4 两数组中位数 | 两个有序数组 | 二分分割线 | `total_left` 和四个边界值 | O(log(min(m, n))) |

## 常见易错点

第一，区间的开闭和循环条件不配套。右开区间配 `left < right`，闭区间配 `left <= right`。改了一个忘了改另一个是二分最常见的 bug。

第二，更新边界时该不该减一。`mid` 已经确定不是答案，才写 `mid` 加减一；`mid` 还可能是答案，就直接写 `mid`。153 里的 `right = mid` 属于后一种。

第三，返回哪个变量。找具体值返回 `mid` 或者 -1，找位置返回 `left`。区间缩空以后 `left` 和 `right` 一般相等，习惯上统一返回 `left`。

第四，循环会不会结束。区间长度为 1 或者 2 时最容易死循环。检查一下每轮是不是至少有一边真的移动了。

第五，边界条件写全。33 里的范围判断两边都要带等号，34 里要先确认 target 在不在数组里。少写一个条件，代码不会报错，答案会悄悄出错。

## 共同规律

把这六道题放一起看，骨架完全一样，都是定区间、取中点、缩一半这三步。真正有区别的只有一件事，怎么判断该往哪边缩。

| 题目 | 判断缩哪边的依据 |
| --- | --- |
| 35 | `nums[mid]` 和目标比大小 |
| 74 | 先换算成行列，再和目标比大小 |
| 34 | 把判定条件从大于等于改成大于，调用两次 |
| 33 | 先判断哪一半有序，再看目标在不在这一半里 |
| 153 | `nums[mid]` 和右端比大小 |
| 4 | 比较切分点两侧的四个值，看条件满不满足 |

第二个规律是关于「找值」和「找位置」的区分。35、34、153 要的是位置，所以最后返回的是 `left`。74、33 要的是有没有这个值，所以返回 `mid` 或者 -1。写之前先明确题目问的是位置还是值，返回语句就不会写错。

第三个规律是二分的适用条件比看起来宽。它只要求「根据条件能把区间分成含义不同的两半」。数组有序是最常见的一种，旋转数组是一种，两个数组的分割线是一种。只要你能写出一个单调的判断，就能二分。

第四个规律是关于单侧比较。153 和 33 都说明，另一半的信息往往不需要真的去读。153 每次只和右端比，33 每次只看有序的那一半。少读数据，判断更简单，也不容易出错。
