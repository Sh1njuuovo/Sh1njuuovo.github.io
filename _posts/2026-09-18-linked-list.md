---
title: "链表（Linked List）"
date: 2026-09-18 11:50:20 +0800
categories: [算法]
tags: ["LeetCode Hot 100"]
description: >-
  链表题的思路都好想，难在代码写对。这一组的共性就是在有限的几个指针之间做文章，靠哨兵、快慢指针、反转模板这三样东西覆盖大部分题。
---
## 一句话概括

链表题的思路都好想，难在代码写对。这一组的共性就是在有限的几个指针之间做文章，靠哨兵、快慢指针、反转模板这三样东西覆盖大部分题。

## 怎么选工具

- 可能改动头节点，或者要在头部插入 → 哨兵节点
- 找中点、判环、找倒数第 k 个 → 快慢指针
- 整段或分组反转 → 三指针反转，先存 `nxt` 再改 `cur.next`
- 两个链表配合 → 让两个指针走一样长的路，或者先对齐长度
- 按大小顺序合并 → 哨兵加双指针，每次挑小的
- 需要 O(1) 找到某个节点 → 哈希表存节点
- 递归分治 → 快慢指针找中点断开，再合并

## Python 基础：节点和四个模板

### 节点定义

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

### 两个必须分清的写法

```python
cur = cur.next      # 移动指针，结构不变
cur.next = X        # 改动结构，让 cur 指向 X
```

改 `cur.next` 之前，如果后面还要用到原来的下一个节点，必须先存下来。否则那条链就丢了。

### 哨兵节点

```python
dummy = ListNode(0, head)
cur = dummy
# ... 一顿操作
return dummy.next
```

作用是让「头节点」这个特殊情况消失，删除或插入时不用单独判断头部。

### 快慢指针

```python
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
```

循环条件两个都要写，`fast.next.next` 要求 `fast.next` 非空，`fast.next` 这个属性又要求 `fast` 非空。

### 反转模板

```python
def reverse(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next        # 先存后面
        cur.next = prev       # 当前节点指向前一个
        prev = cur            # 前一个前进
        cur = nxt             # 当前前进
    return prev
```

这四行的顺序是固定的，后面的 234、25、148 都建立在这个模板上。

### 本地测试小工具

```python
def build(vals):
    dummy = ListNode()
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next


def to_list(head):
    res = []
    while head:
        res.append(head.val)
        head = head.next
    return res
```

## Hot 100 十四道题

### 160. 相交链表 —— 两个指针走一样长的路

**题干**

给定两个单链表的头节点，返回它们开始相交的节点；没有交点时返回 `None`。相交指共享同一个节点对象，数值相同不代表相交。链表无环，不能改变原结构。

**示例**

两个链表分别为 `4,1` 和 `5,6,1`，之后共享节点 `8,4,5`，返回共享的节点 `8`。

```python
def getIntersectionNode(headA, headB):
    if not headA or not headB:
        return None

    pA, pB = headA, headB
    while pA is not pB:
        pA = pA.next if pA else headB
        pB = pB.next if pB else headA

    return pA
```

- 相交指的是同一个节点对象，不是值相等，所以判断要用 `is`
- 让 `pA` 走完 A 接着走 B，`pB` 走完 B 接着走 A，两条路线长度一样，会在交点相遇
- 不相交时两个指针同时走到 `None`，循环自然结束，不用单独判断
- 另一种写法是先求两个长度，让长的先走差值步再一起走

### 206. 反转链表 —— 三指针模板

**题干**

给定单链表头节点，反转所有节点的连接方向，返回反转后的头节点。

**示例**

链表 `[1,2,3,4,5]` 反转后为 `[5,4,3,2,1]`。

```python
def reverseList(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
```

递归版本：

```python
def reverseList(head):
    if not head or not head.next:
        return head
    new_head = reverseList(head.next)
    head.next.next = head
    head.next = None
    return new_head
```

- 迭代版 O(1) 空间，递归版要 O(n) 栈空间，Python 递归深度上限是 1000，长链表会崩
- 易错：忘记先存 `nxt`，改完 `cur.next` 就找不到后面的链了

### 234. 回文链表 —— 找中点 + 反转后半 + 比较

**题干**

给定单链表，判断节点值从前往后和从后往前是否一致。进阶要求 `O(n)` 时间和 `O(1)` 额外空间。

**示例**

`[1,2,2,1]` 返回 `True`，`[1,2]` 返回 `False`。

```python
def isPalindrome(head):
    # 找中点，slow 停在中间
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # 反转后半部分，prev 成为后半的新的头
    prev = None
    while slow:
        nxt = slow.next
        slow.next = prev
        prev = slow
        slow = nxt

    # 从两端往中间比
    left, right = head, prev
    while right:
        if left.val != right.val:
            return False
        left = left.next
        right = right.next
    return True
```

- 只比较到 `right` 走完就行，奇数长度时中间那个节点不用管
- 易错：比较循环的条件用 `while right`，不能写 `while left and right`，那样奇数长度会多比一次
- 进阶要求是还原链表，做法是再次反转后半段然后接回去

### 141. 环形链表 —— 快慢指针判环

**题干**

给定链表头节点，判断链表中是否有环。若沿 `next` 可以再次到达同一节点，则存在环。输入不直接提供环的位置，进阶要求常数空间。

**示例**

链表 `[3,2,0,-4]` 的尾节点连接到下标 `1` 的节点时，返回 `True`。

```python
def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

- 有环时快指针一定追上慢指针，每轮追近一步，不会跳过
- 没环时快指针先到空

### 142. 环形链表 II —— 相遇后从头再走

**题干**

给定链表，返回环的入口节点；无环时返回 `None`。不能修改链表，输入不直接提供入口位置，进阶要求常数空间。

**示例**

链表 `[3,2,0,-4]` 的尾节点连接到下标 `1` 时，返回该节点对象，其值为 `2`。

```python
def detectCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            p = head
            while p is not slow:
                p = p.next
                slow = slow.next
            return p
    return None
```

- 设头到环入口长 `a`，入口到相遇点长 `b`，相遇点到入口长 `c`。慢走 `a + b`，快走 `a + b + c + b`，快是慢的两倍，推出 `a = c`
- 所以从相遇点继续走 `c` 步和从头部走 `a` 步会同时到入口
- 易错：判断相遇要放在两个指针移动之后，不能放在移动之前

### 21. 合并两个有序链表 —— 哨兵 + 挑小的

**题干**

给定两个按非递减顺序排列的链表，合并成一个仍按非递减顺序排列的链表，返回头节点。合并通过连接原有节点完成。

**示例**

`[1,2,4]` 和 `[1,3,4]` 合并为 `[1,1,2,3,4,4]`。

```python
def mergeTwoLists(list1, list2):
    dummy = ListNode()
    cur = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            cur.next = list1
            list1 = list1.next
        else:
            cur.next = list2
            list2 = list2.next
        cur = cur.next
    cur.next = list1 if list1 else list2
    return dummy.next
```

- 循环结束后把剩下的那条整段接上，不用再逐个搬
- 易错：`cur = cur.next` 要放在 if 外面，两个分支都要前进
- 这题是 23 和 148 的地基

### 2. 两数相加 —— 哨兵 + 进位

**题干**

两个非空链表分别表示非负整数，每个节点存一位数字，低位在前。求两数之和，并按同样的逆序格式返回链表。除数字 `0` 外没有多余的前导零。

**示例**

`[2,4,3]` 表示 `342`，`[5,6,4]` 表示 `465`，结果为 `[7,0,8]`。

```python
def addTwoNumbers(l1, l2):
    dummy = ListNode()
    cur = dummy
    carry = 0
    while l1 or l2 or carry:
        s = carry
        if l1:
            s += l1.val
            l1 = l1.next
        if l2:
            s += l2.val
            l2 = l2.next
        carry, digit = divmod(s, 10)
        cur.next = ListNode(digit)
        cur = cur.next
    return dummy.next
```

- 循环条件里的 `or carry` 不能省，最后可能还有一次进位要补
- 链表是逆序存的，正好方便从低位往高位加
- 易错：忘记处理最高位的进位，比如 5 + 5 要输出 `[0, 1]`

### 19. 删除链表的倒数第 N 个结点 —— 快慢指针

**题干**

给定链表和有效的正整数 `n`，删除倒数第 `n` 个节点，返回新的头节点。进阶要求只遍历一次。

**示例**

`[1,2,3,4,5]`，`n = 2`，删除后为 `[1,2,3,5]`。

```python
def removeNthFromEnd(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy

    for _ in range(n + 1):
        fast = fast.next

    while fast:
        fast = fast.next
        slow = slow.next

    slow.next = slow.next.next
    return dummy.next
```

- 哨兵让「删的正好是头节点」也能统一处理
- 快指针先走 `n + 1` 步，这样 `fast` 到空时 `slow` 正好停在要删节点的前一个
- 易错：走的是 `n + 1` 步，走 `n` 步会让 `slow` 停在要删的节点上，没法删除

### 24. 两两交换链表中的节点

**题干**

给定链表，将相邻节点两两交换，返回新的头节点。只能调整节点连接，不能仅交换节点值。若节点数为奇数，最后一个节点保持原位。

**示例**

`[1,2,3,4]` 变为 `[2,1,4,3]`。

```python
def swapPairs(head):
    dummy = ListNode(0, head)
    prev = dummy

    while prev.next and prev.next.next:
        first = prev.next
        second = first.next

        prev.next = second
        first.next = second.next
        second.next = first

        prev = first

    return dummy.next
```

- 每次处理 `prev` 后面的两个节点，交换完 `prev` 前进到 `first`，也就是新的后半段末尾
- 三条赋值语句的顺序很重要，`prev.next = second` 会覆盖掉原来的 `first`，所以前面要先存好
- 易错：循环条件两个都要写，节点数是奇数时最后一轮只有一个节点，直接跳过

### 25. K 个一组翻转链表

**题干**

给定链表和正整数 `k`，每 `k` 个节点为一组反转。最后不足 `k` 个的节点保持原顺序，不能仅交换节点值；进阶要求常数额外空间。

**示例**

`[1,2,3,4,5]`，`k = 2`，结果为 `[2,1,4,3,5]`。

```python
def reverseKGroup(head, k):
    n = 0
    cur = head
    while cur:
        n += 1
        cur = cur.next

    p0 = dummy = ListNode(next=head)
    pre = None
    cur = p0.next

    while n >= k:
        n -= k

        for _ in range(k):
            nxt = cur.next
            cur.next = pre
            pre = cur
            cur = nxt

        nxt = p0.next
        nxt.next = cur
        p0.next = pre
        p0 = nxt

    return dummy.next
```

- 先遍历一次统计节点数 `n`，只有剩余节点数至少为 `k` 时才反转一组
- `p0` 指向当前组的前一个节点，`cur` 指向待反转节点。组内用 `pre`、`cur`、`nxt` 完成三指针反转
- 反转后，`pre` 是这一组的新头，原来的组头 `p0.next` 变成组尾。先用 `nxt` 保存这个组尾，再让它连接 `cur`，然后让 `p0` 连接 `pre`
- 最后令 `p0 = nxt`，从新的组尾继续处理下一组。不足 `k` 个的尾部保持原顺序
- 这版在组间保留 `pre`，反转过程中可能暂时形成环，但接回时 `nxt.next = cur` 会修正组尾的连接。这一步必须在移动 `p0` 前完成
- 时间复杂度为 `O(n)`，额外空间为 `O(1)`

### 138. 随机链表的复制（暂未做）

**题干**

链表节点除 `next` 外还有 `random` 指针，可指向任意节点或 `None`。返回整条链表的深拷贝，所有节点都要新建，复制后的两个指针都只能指向新链表中的节点或 `None`。

**示例**

两个节点的值为 `1,2`，第一个的 `random` 指向第二个，第二个指向自身。复制后保留这些关系，但两个节点都必须是新对象。

每个节点除了 `next` 还有一个 `random` 指针，指向任意节点或者空。做法一是先用哈希表建立「原节点到新节点」的对应，再统一处理两个指针。

```python
def copyRandomList(head):
    if not head:
        return None

    mapping = {}
    cur = head
    while cur:
        mapping[cur] = Node(cur.val)
        cur = cur.next

    cur = head
    while cur:
        mapping[cur].next = mapping[cur.next] if cur.next else None
        mapping[cur].random = mapping[cur.random] if cur.random else None
        cur = cur.next

    return mapping[head]
```

做法的核心是用「原节点」当哈希 key，这样任何一个指针都能查表找到对应的新节点。

还有一种 O(1) 空间的原地做法，把拷贝节点插到原节点后面，形成 `A → A' → B → B'` 的形状，利用 `cur.random.next` 处理 random，最后把两条链拆开。这个写法更绕，面试里写出哈希版本就够了。

### 148. 排序链表 —— 归并排序

**题干**

给定链表，按节点值升序排序，返回排序后的头节点。进阶要求 `O(n log n)` 时间和常数额外空间。

**示例**

`[4,2,1,3]` 排序后为 `[1,2,3,4]`。

```python
def sortList(head):
    if head is None or head.next is None:
        return head
    head2 = middleNode(head)
    head = sortList(head)
    head2 = sortList(head2)
    return merge(head, head2)


def middleNode(head):
    slow = fast = head
    while fast and fast.next:
        pre = slow
        slow = slow.next
        fast = fast.next.next
    pre.next = None
    return slow


def merge(list1, list2):
    cur = dummy = ListNode()
    while list1 and list2:
        if list1.val < list2.val:
            cur.next = list1
            list1 = list1.next
        else:
            cur.next = list2
            list2 = list2.next
        cur = cur.next
    cur.next = list1 if list1 else list2
    return dummy.next
```

- `sortList` 先处理空链表和单节点，再把链表拆成两段，分别递归排序，最后合并
- `middleNode` 用快慢指针找第二段的头节点 `slow`，用 `pre` 保存它前面的节点，再通过 `pre.next = None` 断开两段
- `middleNode` 只在链表至少有两个节点时调用，所以 `pre` 会在循环中得到赋值。断开操作必须在递归排序前完成
- `merge` 每次连接两段中值较小的节点，一段耗尽后直接连接另一段剩余的节点
- 时间复杂度为 `O(n log n)`，递归栈占用 `O(log n)` 额外空间。进阶的常数空间要求可用自底向上的迭代归并实现

### 23. 合并 K 个升序链表 —— 两两合并

**题干**

给定 `k` 个升序链表，将全部节点合并成一个升序链表，返回其头节点。

**示例**

`[[1,4,5],[1,3,4],[2,6]]` 合并为 `[1,1,2,3,4,4,5,6]`。

```python
def mergeKLists(lists):
    m = len(lists)
    if m == 0:
        return None
    if m == 1:
        return lists[0]
    left = mergeKLists(lists[:m // 2])
    right = mergeKLists(lists[m // 2:])
    return mergeTwoLists(left, right)


def mergeTwoLists(list1, list2):
    cur = dummy = ListNode()  # 用哨兵节点简化代码逻辑
    while list1 and list2:
        if list1.val < list2.val:
            cur.next = list1  # 把 list1 加到新链表中
            list1 = list1.next
        else:  # 相等时连接任意一侧的节点都可以
            cur.next = list2  # 把 list2 加到新链表中
            list2 = list2.next
        cur = cur.next
    cur.next = list1 if list1 else list2  # 拼接剩余链表
    return dummy.next
```

- `mergeKLists` 把链表列表从中间分成两半，分别递归合并，再用 `mergeTwoLists` 合并两个结果
- 没有链表时返回 `None`，只有一条时直接返回它。列表中的链表也可能是 `None`
- `mergeTwoLists` 每次连接值较小的节点，一条链表耗尽后直接连接另一条的剩余部分
- 设 `N` 为节点总数，`k` 为链表条数。合并节点耗时 `O(N log k)`，切片另需 `O(k log k)` 时间
- 切片会复制列表中的节点引用，不会复制链表节点。切片的峰值额外空间为 `O(k)`，递归栈为 `O(log k)`，所以总额外空间为 `O(k)`

### 146. LRU 缓存 —— OrderedDict

**题干**

实现容量为正整数 `capacity` 的 LRU 缓存。`get(key)` 返回已有值并更新使用顺序，缺失时返回 `-1`。`put(key,value)` 写入或更新并标记为最近使用，超容量时淘汰最久未使用的键。两种操作都要求平均 `O(1)` 时间。

**示例**

容量为 `2`，先写入键 `1,2`，再读取键 `1`，随后写入键 `3`，此时键 `2` 被淘汰，`get(2)` 返回 `-1`。

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
```

- `OrderedDict` 保存键值和使用顺序。最左端是最近使用的键，最右端是最久未使用的键
- `get` 命中后，用 `move_to_end(key, last=False)` 把键移到最左端，再返回它的值。未命中时返回 `-1`
- `put` 先写入或更新键值，再把键移到最左端。超过容量时，`popitem()` 默认删除最右端的键值对
- `get` 和更新已有键的 `put` 都会刷新使用顺序。`move_to_end` 和 `popitem` 的两端必须保持一致
- `OrderedDict` 在类外导入，供方法直接使用。每次操作平均耗时 `O(1)`，空间为 `O(capacity)`

## 题目分类

| 类型 | 题目 | 核心 |
| --- | --- | --- |
| 指针基础 | 206、24、25 | 先存再改，分组处理 |
| 快慢指针 | 141、142、234、19 | 快走两步慢走一步 |
| 哨兵节点 | 21、2、19、24、25 | 消除头节点的特殊情况 |
| 长度对齐 | 160 | 让两个指针走一样长 |
| 哈希配合 | 146、138 | 用节点当 key |
| 分治 | 23、148 | 找中点断开，再合并 |

## 复杂度

| 题号 | 时间 | 额外空间 |
| --- | --- | --- |
| 160 | O(m + n) | O(1) |
| 206 | O(n) | O(1) |
| 234 | O(n) | O(1) |
| 141 | O(n) | O(1) |
| 142 | O(n) | O(1) |
| 21 | O(m + n) | O(1) |
| 2 | O(max(m, n)) | O(1) |
| 19 | O(n) | O(1) |
| 24 | O(n) | O(1) |
| 25 | O(n) | O(1) |
| 148 | O(n log n) | O(log n) |
| 23 | O((N + k) log k) | O(k) |
| 146 | O(1) 每次操作 | O(capacity) |

## 共同规律

链表题的复杂度基本都是 O(n) 时间和 O(1) 额外空间，剩下的就是代码层面的准确度。这一组反复出现的只有四件事。

- 改指针前先保存原来的指向
- 头节点会变就用哨兵
- 位置类问题就用快慢指针
- 分组和区间操作先把边界定清楚，再动指针

写的时候照着「先断哪条，再接哪条」的顺序一步一步来，别一口气写三条赋值。面试里如果卡住，先在纸上画出两三个节点和指针，比盯着代码想更快。
