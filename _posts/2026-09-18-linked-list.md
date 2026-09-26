---
title: "链表（Linked List）"
date: 2026-09-18 11:50:20 +0800
categories: [算法]
tags: [刷题]
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

```python
def reverseKGroup(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy

    while True:
        # 先看后面还有没有 k 个节点
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next

        group_next = kth.next

        # 翻转 group_prev.next 到 kth 这一段
        prev, cur = group_next, group_prev.next
        for _ in range(k):
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt

        new_group_prev = group_prev.next
        group_prev.next = kth
        group_prev = new_group_prev
```

- 三步循环，先数够不够 k 个，再翻转，最后接回去
- 翻转前把 `prev` 设成 `group_next`，这样翻转完这一段直接接到后面
- 易错：`new_group_prev` 必须在 `group_prev.next = kth` 之前取，改完就找不到了
- 不足 k 个的那一段保持原样，所以数不够时直接返回

### 138. 随机链表的复制（暂未做）

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

```python
def sortList(head):
    if not head or not head.next:
        return head

    # 快慢指针找中点，断开成两段
    slow, fast = head, head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    mid = slow.next
    slow.next = None

    left = sortList(head)
    right = sortList(mid)
    return merge(left, right)


def merge(a, b):
    dummy = ListNode()
    cur = dummy
    while a and b:
        if a.val <= b.val:
            cur.next = a
            a = a.next
        else:
            cur.next = b
            b = b.next
        cur = cur.next
    cur.next = a if a else b
    return dummy.next
```

- 快慢指针初始化成 `head` 和 `head.next`，这样偶数长度时中点偏左，两段长度差不超过 1
- 断开那一步 `slow.next = None` 必须写，否则递归不会终止
- 递归深度是 O(log n)，不会碰到 Python 的递归上限

### 23. 合并 K 个升序链表 —— 两两合并

```python
def mergeKLists(lists):
    if not lists:
        return None

    def merge(a, b):
        dummy = ListNode()
        cur = dummy
        while a and b:
            if a.val <= b.val:
                cur.next = a
                a = a.next
            else:
                cur.next = b
                b = b.next
            cur = cur.next
        cur.next = a if a else b
        return dummy.next

    def divide(lo, hi):
        if lo == hi:
            return lists[lo]
        mid = (lo + hi) // 2
        return merge(divide(lo, mid), divide(mid + 1, hi))

    return divide(0, len(lists) - 1)
```

- 分治合并，总时间 O(N log k)，`N` 是节点总数，`k` 是链表条数
- 易错：`lists` 可能是空列表，也可能里面有 `None`，边界要处理
- 另一种做法是把 `k` 个表头放进小顶堆，每次弹最小的那个，适合 `k` 很大的场景

### 146. LRU 缓存 —— 哈希表 + 双向链表

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = {}
        self.head = Node()          # 哨兵，head.next 是最近使用的
        self.tail = Node()          # 哨兵，tail.prev 是最久未使用的
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.cap:
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)
```

- 哈希表负责 O(1) 找到节点，双向链表负责维护使用顺序
- 两个哨兵让「链表为空」和「删的是头或尾」都不用特判
- 节点里必须存 `key`，淘汰时要用它去删哈希表里的那一项
- 易错：`get` 命中之后也要把节点移到头部，因为访问算作使用
- 易错：容量为 1 时先删再加，顺序反了会把刚放进去的节点删掉

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
| 23 | O(N log k) | O(log k) |
| 146 | O(1) 每次操作 | O(capacity) |

## 共同规律

链表题的复杂度基本都是 O(n) 时间和 O(1) 额外空间，剩下的就是代码层面的准确度。这一组反复出现的只有四件事。

- 改指针前先保存原来的指向
- 头节点会变就用哨兵
- 位置类问题就用快慢指针
- 分组和区间操作先把边界定清楚，再动指针

写的时候照着「先断哪条，再接哪条」的顺序一步一步来，别一口气写三条赋值。面试里如果卡住，先在纸上画出两三个节点和指针，比盯着代码想更快。
