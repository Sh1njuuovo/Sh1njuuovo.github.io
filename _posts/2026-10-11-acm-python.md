---
title: "Python ACM 输入输出与 Hot 100 例题"
date: 2026-10-11 00:00:00 +0800
categories: [算法, 数据结构与算法]
tags: ["LeetCode Hot 100", "ACM 输入输出", Python]
description: >-
  只用 input() 和 print()，整理最常用的 ACM 读写方式和九个完整程序。
---
LeetCode 通常替你构造参数并调用核心函数。ACM 格式需要自己读取标准输入、构造参数、调用算法，并把结果写到标准输出。算法主体通常可以保留，主要补上程序入口和输入输出处理。

[返回算法索引](/posts/algorithm-index/)

本文使用 Python 3。下面为 Hot 100 代表题自定义了输入输出约定，用来练习完整程序；实际提交时请按题面的格式调整。

## 记住这一套就够了

读入用 `input()`，输出用 `print()`。先定义核心函数，再在文件末尾读入参数、调用函数、打印结果，不必额外写 `main()`。

```python
n = int(input())                         # 一个整数
n, k = map(int, input().split())          # 一行多个整数
nums = list(map(int, input().split()))    # 一行整数数组
s = input()                              # 一行字符串
matrix = [list(map(int, input().split())) for _ in range(n)]

print(ans)                               # 一个答案
print(*nums)                             # 数组，空格分隔
for row in matrix:
    print(*row)                          # 矩阵，每行一次输出
```

这些是独立的常用写法，按题目选择需要的几行。`input()` 自动去掉行末换行，但保留字符串中的空格。`.split()` 按空白拆分，`map(int, ...)` 把每项转成整数，外面的 `list(...)` 得到数组。

### 多组输入

首行给出组数时：

```python
T = int(input())
for _ in range(T):
    n = int(input())
    nums = list(map(int, input().split()))
    # 这里计算并 print 答案
```

没有组数，需要读到文件结束时：

```python
while True:
    try:
        n = int(input())
    except EOFError:
        break
    # 这里计算并 print 答案
```

每组重新读入和计算。EOF 写法只捕获输入结束，不把数据格式错误当成正常结束。

普通核心函数不需要 `self`。链表和二叉树要先建节点，LRU 这类多次操作同一个对象的题目保留类。数组用 `print(*ans)`，布尔结果按题面打印 `YES` 或 `NO`。不要输出提示语和调试信息。

## 代表题完整程序

### 1. 两数之和

[查看核心题解](/posts/hashmap/#1-两数之和--补数配对)

**输入输出约定**

第一行是数组长度 `n` 和目标值 `target`，第二行给出 `n` 个整数。输出两个下标，用空格分隔，下标从 `0` 开始。保证存在唯一答案。

**样例输入**

```text
4 9
2 7 11 15
```

**样例输出**

```text
0 1
```

**完整程序**

```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []


n, target = map(int, input().split())
nums = list(map(int, input().split()))
print(*two_sum(nums, target))
```

数组放在一行读入，最后直接 `print(*答案)`。

### 53. 最大子数组和，多组输入

[查看核心题解](/posts/array/#53-最大子数组和--一次遍历维护状态)

**输入输出约定**

第一个整数是测试组数 `T`。每组先给数组长度 `n`，下一行给 `n` 个整数。每组输出一个最大和，独占一行，数组非空。

**样例输入**

```text
2
9
-2 1 -3 4 -1 2 1 -5 4
3
-3 -2 -5
```

**样例输出**

```text
6
-2
```

**完整程序**

```python
def max_subarray(nums):
    current = best = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)
        best = max(best, current)
    return best


T = int(input())
for _ in range(T):
    n = int(input())
    nums = list(map(int, input().split()))
    print(max_subarray(nums))
```

每组读入长度和一行数组，计算后立即输出。

### 70. 爬楼梯，读到 EOF

[查看核心题解](/posts/dp/#70-爬楼梯)

**输入输出约定**

每行一个正整数 `n`，直到文件结束。对每个 `n` 输出走法总数，独占一行。练习约定 `1 <= n <= 45`。

**样例输入**

```text
2
3
5
```

**样例输出**

```text
2
3
8
```

**完整程序**

```python
def climb_stairs(n):
    a = b = 1
    for _ in range(n):
        a, b = b, a + b
    return a


while True:
    try:
        n = int(input())
    except EOFError:
        break
    print(climb_stairs(n))
```

每行一个整数，读到 EOF 就结束。

### 3. 无重复字符的最长子串

[查看核心题解](/posts/sliding-window/#3-无重复字符的最长子串--变长窗口)

**输入输出约定**

输入一行字符串，允许空字符串和空格。输出最长无重复连续子串长度。空格也视为字符，不能删掉。

**样例输入**

```text
abcabcbb
```

**样例输出**

```text
3
```

**完整程序**

```python
def length_of_longest_substring(s):
    last = {}
    left = best = 0
    for right, ch in enumerate(s):
        left = max(left, last.get(ch, -1) + 1)
        last[ch] = right
        best = max(best, right - left + 1)
    return best


s = input()
print(length_of_longest_substring(s))
```

直接用 `input()`，空字符串和首尾空格都能保留。

### 54. 螺旋矩阵

[查看核心题解](/posts/matrix/#54-螺旋矩阵--方向数组--访问标记)

**输入输出约定**

前两个整数是行数 `m` 和列数 `n`，接着每行给出 `n` 个整数，共 `m` 行。矩阵非空，输出螺旋顺序，用空格分隔。

**样例输入**

```text
3 3
1 2 3
4 5 6
7 8 9
```

**样例输出**

```text
1 2 3 6 9 8 7 4 5
```

**完整程序**

```python
def spiralOrder(matrix):
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    m, n = len(matrix), len(matrix[0])
    ans = []
    i = j = di = 0
    for _ in range(m * n):
        ans.append(matrix[i][j])
        matrix[i][j] = None
        x, y = i + dirs[di][0], j + dirs[di][1]
        if x < 0 or x >= m or y < 0 or y >= n or matrix[x][y] is None:
            di = (di + 1) % 4
        i += dirs[di][0]
        j += dirs[di][1]
    return ans


m, n = map(int, input().split())
matrix = [list(map(int, input().split())) for _ in range(m)]
print(*spiralOrder(matrix))
```

先读行列数，再逐行读矩阵。

### 206. 反转链表

[查看核心题解](/posts/linked-list/#206-反转链表--三指针模板)

**输入输出约定**

先给节点数 `n`，第二行给 `n` 个节点值，空链表时第二行留空。输出反转后的节点值，用空格分隔。`n = 0` 表示空链表，输出空行。

**样例输入**

```text
5
1 2 3 4 5
```

**样例输出**

```text
5 4 3 2 1
```

**完整程序**

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    tail = dummy = ListNode()
    for value in values:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next


def reverseList(head):
    pre = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = pre
        pre = cur
        cur = nxt
    return pre


n = int(input())
values = list(map(int, input().split()))
head = reverseList(build_list(values))
ans = []
while head:
    ans.append(head.val)
    head = head.next
print(*ans)
```

读入一行节点值，建链表后调用核心函数，最后输出节点值。

### 102. 二叉树的层序遍历

[查看核心题解](/posts/binary-tree/#102-二叉树的层序遍历--形状二)

**输入输出约定**

输入一行层序序列，用空格分隔，`null` 表示缺失节点。依次为队列中每个非空节点读取左右孩子，可省略末尾的 `null`。空树输入 `null`。输出每层节点值，每层一行；空树输出 `EMPTY`。

**样例输入**

```text
3 9 20 null null 15 7
```

**样例输出**

```text
3
9 20
15 7
```

**完整程序**

```python
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    if not values or values[0] == "null":
        return None
    root = TreeNode(int(values[0]))
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if values[i] != "null":
            node.left = TreeNode(int(values[i]))
            queue.append(node.left)
        i += 1
        if i < len(values):
            if values[i] != "null":
                node.right = TreeNode(int(values[i]))
                queue.append(node.right)
            i += 1
    return root


def levelOrder(root):
    if root is None:
        return []
    queue = deque([root])
    ans = []
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        ans.append(level)
    return ans


values = input().split()
levels = levelOrder(build_tree(values))
if not levels:
    print("EMPTY")
else:
    for level in levels:
        print(*level)
```

先把 `null` 层序序列建成树，再逐层输出。

### 207. 课程表

[查看核心题解](/posts/graph/#207-课程表--拓扑排序)

**输入输出约定**

第一行是课程数 `n` 和先修关系数 `m`，接着给出 `m` 对整数 `a b`，表示学 `a` 前必须完成 `b`。课程编号从 `0` 开始。能完成全部课程输出 `YES`，否则输出 `NO`。

**样例输入**

```text
2 1
1 0
```

**样例输出**

```text
YES
```

**完整程序**

```python
from collections import deque


def canFinish(n, prerequisites):
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for a, b in prerequisites:
        graph[b].append(a)
        indegree[a] += 1
    queue = deque(i for i in range(n) if indegree[i] == 0)
    completed = 0
    while queue:
        node = queue.popleft()
        completed += 1
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return completed == n


n, m = map(int, input().split())
prerequisites = [list(map(int, input().split())) for _ in range(m)]
print("YES" if canFinish(n, prerequisites) else "NO")
```

每行读一条先修关系，最后输出 `YES` 或 `NO`。

### 146. LRU 缓存

[查看核心题解](/posts/linked-list/#146-lru-缓存--ordereddict)

**输入输出约定**

第一行是正整数容量 `capacity` 和操作数 `q`。随后每行是 `put key value` 或 `get key`。仅为 `get` 输出结果，每个结果一行，未命中输出 `-1`。

**样例输入**

```text
2 6
put 1 1
put 2 2
get 1
put 3 3
get 2
get 3
```

**样例输出**

```text
1
-1
3
```

**完整程序**

```python
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key, last=False)
        return self.cache[key]

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key, last=False)
        if len(self.cache) > self.capacity:
            self.cache.popitem()


capacity, q = map(int, input().split())
cache = LRUCache(capacity)
for _ in range(q):
    parts = input().split()
    if parts[0] == "put":
        cache.put(int(parts[1]), int(parts[2]))
    else:
        print(cache.get(int(parts[1])))
```

每行读一个命令，只有 `get` 需要输出。

## 本地运行

把完整程序存成 `main.py`，样例输入存成 `input.txt`，运行：

```bash
python3 main.py < input.txt
```

检查输出是否与样例一致即可。
