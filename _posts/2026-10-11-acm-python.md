---
title: "Python ACM 输入输出与 Hot 100 例题"
date: 2026-10-11 00:00:00 +0800
categories: [算法]
tags: ["LeetCode Hot 100", "ACM 输入输出", Python]
description: >-
  从核心函数到完整程序，整理单组、多组、EOF 输入，以及数组、矩阵、链表、二叉树和操作序列的九个可运行例子。
---
LeetCode 通常替你构造参数并调用核心函数。ACM 格式需要自己读取标准输入、构造参数、调用算法，并把结果写到标准输出。算法主体通常可以保留，主要补上程序入口和输入输出处理。

[返回算法索引](/posts/algorithm-index/)

本文使用 Python 3。下面为 Hot 100 代表题自定义了输入输出约定，用来练习完整程序；实际提交时请按题面的格式调整。

## 完整程序由哪些部分组成

1. 导入用到的标准库。
2. 定义核心函数，链表和二叉树题还需要定义节点。
3. 在 `main()` 中读取输入，构造函数参数，调用算法并输出结果。
4. 用 `if __name__ == "__main__":` 调用 `main()`。

普通函数不需要 `self`。从 `Solution` 类中取出核心方法时，将 `self.helper(...)` 改为普通函数调用。如果题目要求多次操作同一对象，例如 LRU 缓存，就保留类。

输入中的数组通常是空格分隔的数字，不带 Python 的方括号。不要用 `eval()` 解析输入。题目如果明确采用 JSON，可以用 `json.loads()`。

## 先判断输入属于哪一种

| 输入形态 | 读法 | 例子 |
| --- | --- | --- |
| 单组数字和数组 | 按空白读取，按长度取元素 | 1 两数之和 |
| 首行给测试组数 | 读取 `T` 后处理恰好 `T` 组 | 53 最大子数组和 |
| 没有组数，读到 EOF | 遍历输入行或按格式取完整一组 | 70 爬楼梯 |
| 完整字符串 | 读一行，仅去除换行 | 3 最长无重复子串 |
| 二维矩阵 | 读取行列数，再构造每行 | 54 螺旋矩阵 |
| 链表 | 读取节点值后建链表 | 206 反转链表 |
| 二叉树 | 读取层序序列，处理 `null` | 102 层序遍历 |
| 图的边列表 | 读取节点数、边数和每条边 | 207 课程表 |
| 操作序列 | 创建对象后逐行执行命令 | 146 LRU 缓存 |

## 输入输出常用写法

### 按行读取和按空白读取

`sys.stdin.readline()` 保留一行的边界，适合字符串或每行一条命令。读到 EOF 时返回空字符串 `""`，真正的空行一般是 `"\n"`。

`sys.stdin.buffer.read().split()` 一次读取全部输入并按空白拆分，适合题面只关心数字顺序的情况。返回的是 `bytes`，可以直接传给 `int()`。这会把全部输入放进内存，特别大的输入或交互题应按行、按需读取。

`map(int, ...)` 是迭代器。要按下标访问时转成 `list`；按顺序取值时可以用 `next()`。长度 `n` 应控制恰好读取几个元素，不能把后续测试组也当作当前数组。

### 多组输入与 EOF

题面给出 `T` 时，循环恰好 `T` 次。题面要求读到 EOF 时，循环到输入结束。每组的计数器、容器和算法状态要重新初始化。

是否跳过空行由输入约定决定。数字输入通常可以跳过空行，字符串题可能将空行视为长度为零的字符串。不要一律跳过。

### 输出列表、矩阵和布尔结果

`print(*values)` 输出空格分隔的一行元素；不要直接 `print(values)`，除非题目明确要求带方括号的格式。二维结果通常逐行 `print(*row)`。

布尔值按题面转换成 `YES/NO`、`true/false` 或 `1/0`，大小写也需要一致。空结果可能要求空行、`EMPTY` 或 `-1`，本文每题单独约定。

很多行结果可以先转成字符串，最后用 `"\n".join(output)` 一次输出。不要输出提示语、调试信息或函数的 `None` 返回值。

## 代表题完整程序

### 1. 两数之和

[查看核心题解](/posts/hashmap/#1-两数之和--补数配对)

**输入输出约定**

第一行是数组长度 `n` 和目标值 `target`，后面给出 `n` 个整数。输出两个下标，用空格分隔，下标从 `0` 开始。保证存在唯一答案。

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
import sys


def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []


def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, target = data[:2]
    nums = data[2:2 + n]
    print(*two_sum(nums, target))


if __name__ == "__main__":
    main()
```

数组元素可以跨行，按空白拆分后结果相同。`print(*ans)` 输出空格分隔的元素。

### 53. 最大子数组和，多组输入

[查看核心题解](/posts/array/#53-最大子数组和--一次遍历维护状态)

**输入输出约定**

第一个整数是测试组数 `T`。每组先给数组长度 `n`，再给 `n` 个整数。每组输出一个最大和，独占一行，数组非空。

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
import sys


def max_subarray(nums):
    current = best = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)
        best = max(best, current)
    return best


def main():
    tokens = iter(map(int, sys.stdin.buffer.read().split()))
    t = next(tokens)
    output = []
    for _ in range(t):
        n = next(tokens)
        nums = [next(tokens) for _ in range(n)]
        output.append(str(max_subarray(nums)))
    sys.stdout.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
```

每组都重新创建数组和算法状态。全为负数时答案是最大的负数，所以不能把最大和初始化为 `0`。

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
import sys


def climb_stairs(n):
    a = b = 1
    for _ in range(n):
        a, b = b, a + b
    return a


def main():
    output = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        output.append(str(climb_stairs(int(line))))
    if output:
        sys.stdout.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
```

这里的空行不是一组数据，可以跳过。读取到 EOF 时循环自然结束，不需要用异常吞掉格式错误。

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
import sys


def length_of_longest_substring(s):
    last = {}
    left = best = 0
    for right, ch in enumerate(s):
        left = max(left, last.get(ch, -1) + 1)
        last[ch] = right
        best = max(best, right - left + 1)
    return best


def main():
    s = sys.stdin.readline().rstrip("\r\n")
    print(length_of_longest_substring(s))


if __name__ == "__main__":
    main()
```

只去掉行末换行。使用 `.strip()` 会删掉首尾空格，使用 `.split()` 会拆散字符串。输入为空行时输出 `0`。

### 54. 螺旋矩阵

[查看核心题解](/posts/matrix/#54-螺旋矩阵--方向数组--访问标记)

**输入输出约定**

前两个整数是行数 `m` 和列数 `n`，接着按行给出 `m * n` 个整数。矩阵非空，输出螺旋顺序，用空格分隔。

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
import sys


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


def main():
    tokens = iter(map(int, sys.stdin.buffer.read().split()))
    m, n = next(tokens), next(tokens)
    matrix = [[next(tokens) for _ in range(n)] for _ in range(m)]
    print(*spiralOrder(matrix))


if __name__ == "__main__":
    main()
```

用列表推导式分别创建每一行。这份实现沿用矩阵笔记中的方向数组写法，会将访问过的位置改为 `None`。

### 206. 反转链表

[查看核心题解](/posts/linked-list/#206-反转链表--三指针模板)

**输入输出约定**

先给节点数 `n`，再给 `n` 个节点值。输出反转后的节点值，用空格分隔。`n = 0` 表示空链表，输出空行。

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
import sys


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


def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    head = build_list(data[1:1 + n])
    head = reverseList(head)
    output = []
    while head:
        output.append(head.val)
        head = head.next
    print(*output)


if __name__ == "__main__":
    main()
```

输入中的数字需要先构造成节点，算法操作节点的 `next`，输出时再沿链表取值。

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
import sys
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


def main():
    root = build_tree(sys.stdin.readline().split())
    levels = levelOrder(root)
    if not levels:
        print("EMPTY")
    else:
        for level in levels:
            print(*level)


if __name__ == "__main__":
    main()
```

这是按队列展开的层序格式。存在缺失节点时，不能直接按数组下标 `2*i+1`、`2*i+2` 连接孩子。例如 `1 null 2 3` 中，`3` 是节点 `2` 的左孩子。

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
import sys
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


def main():
    tokens = iter(map(int, sys.stdin.buffer.read().split()))
    n, m = next(tokens), next(tokens)
    prerequisites = [[next(tokens), next(tokens)] for _ in range(m)]
    print("YES" if canFinish(n, prerequisites) else "NO")


if __name__ == "__main__":
    main()
```

核心函数返回布尔值，`main()` 按约定转换为 `YES` 或 `NO`。读到的 `a b` 对应图中的边 `b` 到 `a`。

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
import sys
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


def main():
    capacity, q = map(int, sys.stdin.readline().split())
    cache = LRUCache(capacity)
    output = []
    for _ in range(q):
        parts = sys.stdin.readline().split()
        if parts[0] == "put":
            cache.put(int(parts[1]), int(parts[2]))
        else:
            output.append(str(cache.get(int(parts[1]))))
    if output:
        sys.stdout.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
```

这个例子需要保留类，因为多个操作共享同一份缓存状态。`put` 没有返回值，也不输出额外的 `None`。

## 如何在本地运行

将某个例子的完整程序保存为 `main.py`，将它的样例输入保存为 `input.txt`，然后运行：

```bash
python3 main.py < input.txt
```

检查实际输出与样例输出是否一致。手动在终端输入时，EOF 是结束输入的信号，具体按键取决于终端；使用文件重定向更方便重复检查。

## 提交前检查

- 是否有测试组数，数组长度和矩阵尺寸是否正确读取。
- 字符串的空格和空行是否按题意保留。
- 链表和二叉树是否已经构造为节点，空结构如何表示。
- 核心函数是否会修改输入，下一组是否复用了旧状态。
- 输出是否符合大小写、分隔符、空结果和换行约定。
- 递归算法是否可能遇到很深的树或很长的路径。必要时改成迭代实现；单纯调大递归上限也会增加栈风险。

这些例子重点是完整程序的组织。需要复习算法时，可以从[算法索引](/posts/algorithm-index/)进入对应专题。
