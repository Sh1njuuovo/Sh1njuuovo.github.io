---
title: "二叉树（Binary Tree）"
date: 2026-09-20 10:58:50 +0800
categories: [算法]
tags: ["LeetCode Hot 100"]
description: >-
  树题的下标和指针都不复杂，复杂的是「递归函数该返回什么」。把这一件事定下来，代码基本就出来了。Hot 100 的十五道树题，按递归形状归类只有六种写法。
---
## 一句话概括

树题的下标和指针都不复杂，复杂的是「递归函数该返回什么」。把这一件事定下来，代码基本就出来了。Hot 100 的十五道树题，按递归形状归类只有六种写法。

## 核心框架：递归形状

拿到一道树题，先问一句「这个递归函数的返回值，有人需要吗」。

### 形状一，遍历，就地修改

```python
def dfs(node):
    if not node:
        return
    对 node 做点事
    dfs(node.left)
    dfs(node.right)
```

递归只是用来走遍所有节点，返回值没人要。代表题是 226 翻转二叉树、114 展开为链表。

### 形状二，遍历，往外部容器收集

```python
res = []

def dfs(node):
    if not node:
        return
    按某种顺序把 node.val 塞进 res
    dfs(node.left)
    dfs(node.right)
```

和形状一一样不返回东西，区别是信息收集到外部容器里。代表题是 94 中序、102 层序、199 右视图、230 第 K 小。

### 形状三，自底向上，返回值就是答案

```python
def dfs(node):
    if not node:
        return 基础值
    left = dfs(node.left)
    right = dfs(node.right)
    return 用 left 和 right 组合出的结果
```

必须接住返回值，因为当前节点的答案由子树的答案算出来。代表题是 104 深度、101 对称、236 最近公共祖先。

### 形状四，自底向上，返回值是中间量

```python
best = 初始值

def dfs(node):
    if not node:
        return 基础值
    left = dfs(node.left)
    right = dfs(node.right)
    best = max(best, 用 left 和 right 算出的拐弯答案)
    return 只能选一边的直路值
```

拐弯的路径在拐弯处就结束了，用来更新全局答案。返回给上层的必须是一条能继续接的直路。代表题是 543 直径、124 最大路径和。

### 形状五，自顶向下，带着约束或状态往下传

```python
def dfs(node, 传来的信息):
    if not node:
        return
    处理当前节点
    dfs(node.left, 新信息)
    dfs(node.right, 新信息)
```

信息从祖先流向叶子。代表题是 98 验证 BST 传区间、437 路径和传前缀和。

### 形状六，分治构造

```python
def build(lo, hi):
    if lo > hi:
        return None
    找到根的位置
    递归构造左右子树
    return 这个根
```

代表题是 105 前序中序构造、108 有序数组转 BST。

## Python 基础

### 节点定义

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

### 三种深度优先遍历

```python
def preorder(node):          # 自己 → 左 → 右
    if not node:
        return
    处理(node)
    preorder(node.left)
    preorder(node.right)


def inorder(node):           # 左 → 自己 → 右
    if not node:
        return
    inorder(node.left)
    处理(node)
    inorder(node.right)


def postorder(node):         # 左 → 右 → 自己
    if not node:
        return
    postorder(node.left)
    postorder(node.right)
    处理(node)
```

选择哪一个，看信息往哪个方向流。

- 需要把信息从上面带下来，用前序
- 需要把信息从下面收上来，用后序
- 在 BST 上要按顺序处理，用中序

### 层序遍历

```python
from collections import deque

def levelOrder(root):
    if not root:
        return []
    res = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):      # 关键，先记下这一层的节点数
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        res.append(level)
    return res
```

`for _ in range(len(queue))` 是所有分层问题的基础。

### 中序遍历的迭代模板

```python
def inorderTraversal(root):
    res, stack, cur = [], [], root
    while cur or stack:
        while cur:                  # 一路向左，沿途压栈
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()           # 弹出就是中序的下一个
        res.append(cur.val)
        cur = cur.right
    return res
```

前序和中序只差 `res.append` 的位置。前序在入栈时记录，中序在出栈时记录。

### 本地测试建树

```python
from collections import deque

def build_tree(vals):
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    q = deque([root])
    i = 1
    while q and i < len(vals):
        node = q.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            q.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            q.append(node.right)
        i += 1
    return root
```

### 两个易错细节

Python 默认递归深度上限是 1000。树退化成链时节点数可能上万，可以用 `sys.setrecursionlimit(10000)` 提高上限。

嵌套函数里修改外层变量，必须写 `nonlocal`。

### 两种写递归的形式

LeetCode 上同一道树题，通常能写成下面两种样子。用 226 翻转二叉树做例子。

形式 A，递归方法自己。

```python
class Solution:
    def invertTree(self, root):
        if root is None:
            return None
        root.left, root.right = root.right, root.left
        self.invertTree(root.left)      # 方法在类里，所以要带 self
        self.invertTree(root.right)
        return root
```

形式 B，在方法里再定义一个嵌套函数。

```python
class Solution:
    def invertTree(self, root):
        def dfs(node):                  # 本地函数，直接写名字就能调
            if node is None:
                return
            node.left, node.right = node.right, node.left
            dfs(node.left)
            dfs(node.right)
        dfs(root)                       # 记得先调用，递归才会跑
        return root
```

两者的区别只有两点。

- 调用的名字不同，形式 A 要用 `self.invertTree`，形式 B 直接用 `dfs`
- 信息传递方式不同，形式 B 一般靠 `nonlocal` 改外层变量，形式 A 一般靠返回值

两种都正确，选哪种看你要不要往上返回信息。形状三和形状四需要返回值，形式 A 写起来更顺。形状一和形状二不需要返回值，形式 B 更干净，因为不用反复写 `self`。

形式 B 的定义写在方法内部，只能在这个方法里用。好处是能直接读到外层的 `res`、`best` 这些变量，坏处是调试时要记得它属于谁。

## Hot 100 十五道题

### 226. 翻转二叉树 —— 形状一

```python
def invertTree(root):
    if not root:
        return None
    root.left, root.right = root.right, root.left
    invertTree(root.left)
    invertTree(root.right)
    return root
```

- 每个节点交换自己的左右孩子，递归负责走遍全树
- 递归调用不需要接返回值，因为交换是原地生效的
- 也可以写成自底向上的版本，先 `left = invertTree(root.left)`，再重新挂上去，结果一样
- 这题正好是「形式 A 还是形式 B」最典型的例子，对比见前面的小节
- 易错：只交换根节点就返回，忘记递归

### 114. 展开为链表 —— 形状一

```python
def flatten(root):
    cur = root
    while cur:
        if cur.left:
            pre = cur.left
            while pre.right:          # 找左子树的最右节点
                pre = pre.right
            pre.right = cur.right     # 原来的右子树接到尾巴后面
            cur.right = cur.left      # 左子树整块搬到右边
            cur.left = None           # 左指针清空
        cur = cur.right
```

- 先序遍历的最后一个节点，是从根一路往右走到底的那个
- 三行顺序固定，先接右边，再搬左边，最后清空
- 易错：顺序写反会让原来的右子树丢失；`cur = cur.right` 要放在 `if` 外面，每轮都要前进

### 94. 二叉树的中序遍历 —— 形状二

```python
def inorderTraversal(root):
    res = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        res.append(node.val)
        dfs(node.right)
    dfs(root)
    return res
```

- 递归三行的顺序和「左根右」的定义完全一致
- 迭代版本见上面的中序模板，栈的作用是记住回去的路
- 易错：递归版写成 `return dfs(root.left) + [root.val] + dfs(root.right)` 会反复新建列表，效率差

### 102. 二叉树的层序遍历 —— 形状二

```python
from collections import deque

def levelOrder(root):
    if not root:
        return []
    res = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        res.append(level)
    return res
```

- 内层循环的边界必须在进循环前算好，用的是当前队列长度
- 易错：直接 `while queue` 出队，就分不出层了

### 199. 二叉树的右视图 —— 形状二

```python
from collections import deque

def rightSideView(root):
    if not root:
        return []
    res = []
    queue = deque([root])
    while queue:
        size = len(queue)
        for i in range(size):
            node = queue.popleft()
            if i == size - 1:          # 这一层最后一个
                res.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return res
```

另一种写法是深度优先，先走右子树，用 `depth == len(res)` 判断这一层是不是第一次到达。

```python
def rightSideView(root):
    res = []
    def dfs(node, depth):
        if not node:
            return
        if depth == len(res):          # 这一层还没记录过
            res.append(node.val)
        dfs(node.right, depth + 1)     # 先右后左
        dfs(node.left, depth + 1)
    dfs(root, 0)
    return res
```

- 易错：层序版判断写成 `i == 0` 是左视图；深度优先版没有优先走右边也会变成左视图

### 230. BST 中第 K 小的元素 —— 形状二加中序

```python
def kthSmallest(root, k):
    stack, cur = [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right
```

- BST 的中序严格递增，第 k 小就是中序序列的第 k 个
- 数到第 k 个立刻返回，不需要遍历完整棵树
- 易错：`k` 从 1 开始计数；`k -= 1` 要在弹出之后立刻做
- 进阶：如果树频繁增删，可以在每个节点记录子树大小，查询降到 O(h)

### 104. 二叉树的最大深度 —— 形状三

```python
def maxDepth(root):
    if not root:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```

- 定义清楚函数含义，代码就是定义的直译
- 返回的是节点数，叶子节点深度是 1
- 易错：空节点返回 1；把深度和边数搞混

### 101. 对称二叉树 —— 形状三，两棵树同步递归

```python
def isSymmetric(root):
    if not root:
        return True
    def check(p, q):
        if not p and not q:
            return True
        if not p or not q:
            return False
        return (p.val == q.val
                and check(p.left, q.right)
                and check(p.right, q.left))
    return check(root.left, root.right)
```

- 镜像的配对方式是 `p.left` 对 `q.right`，`p.right` 对 `q.left`
- 相同树的配对方式是 `p.left` 对 `q.left`，`p.right` 对 `q.right`，两题对比着记
- 易错：写成「相同」的配对，`[1,2,2,null,3,null,3]` 这类结构会被误判

### 236. 二叉树的最近公共祖先 —— 形状三

```python
def lowestCommonAncestor(root, p, q):
    if not root or root is p or root is q:
        return root
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    if left and right:
        return root           # p 和 q 分处两侧，当前节点是答案
    return left if left else right
```

- 返回值有三种含义，已经确定的答案、只找到的一个节点、什么都没找到
- 「一个节点可以是自己的祖先」让提前返回成立
- 易错：用 `root.val == p.val` 比较，应该用 `is` 判断身份

### 543. 二叉树的直径 —— 形状四

```python
def diameterOfBinaryTree(root):
    best = 0
    def dfs(node):
        nonlocal best
        if not node:
            return 0
        left = dfs(node.left)
        right = dfs(node.right)
        best = max(best, left + right)      # 经过当前节点的最长路径
        return 1 + max(left, right)         # 往上返回子树高度
    dfs(root)
    return best
```

- `left + right` 是以当前节点为最高点的路径长度
- 直径算的是边数，子树高度数值正好等于从当前节点往下走的边数
- 易错：返回值写成 `left + right`，那是一条拐弯路径，上层接不了

### 124. 二叉树中的最大路径和 —— 形状四

```python
def maxPathSum(root):
    best = float('-inf')
    def dfs(node):
        nonlocal best
        if not node:
            return 0
        left = max(dfs(node.left), 0)
        right = max(dfs(node.right), 0)
        best = max(best, node.val + left + right)
        return node.val + max(left, right)
    dfs(root)
    return best
```

- 和 543 是同一个骨架，区别只在算的东西
- `max(..., 0)` 处理负数子树，负贡献不如不接
- 易错：`best` 初始化成 0，全负数时会返回错误答案，必须用 `float('-inf')`

### 98. 验证二叉搜索树 —— 形状五

```python
def isValidBST(root):
    def check(node, low, high):
        if not node:
            return True
        if node.val <= low or node.val >= high:
            return False
        return (check(node.left, low, node.val)
                and check(node.right, node.val, high))
    return check(root, float('-inf'), float('inf'))
```

- 区间是开区间，判断用 `<=` 和 `>=`
- 也可以中序遍历，检查是否严格递增
- 易错：只比较节点和它的直接孩子，`[5,1,4,null,null,3,6]` 会被误判成合法

### 437. 路径总和 III —— 形状五加哈希

```python
def pathSum(root, targetSum):
    count = {0: 1}          # 前缀和 -> 出现次数
    res = 0
    def dfs(node, cur):
        nonlocal res
        if not node:
            return
        cur += node.val
        res += count.get(cur - targetSum, 0)    # 先查
        count[cur] = count.get(cur, 0) + 1      # 再存
        dfs(node.left, cur)
        dfs(node.right, cur)
        count[cur] -= 1                         # 回溯
    dfs(root, 0)
    return res
```

- 和 560 和为 K 的子数组是同一套思路，一个在数组上，一个在树上
- `{0: 1}` 表示空前缀和，让从根开始的路径能被统计
- 易错：忘记回溯，左子树的前缀和会污染右子树；先查后存的顺序不能反

### 105. 从前序与中序遍历序列构造二叉树 —— 形状六

```python
def buildTree(preorder, inorder):
    pos = {v: i for i, v in enumerate(inorder)}
    def build(pre_lo, pre_hi, in_lo, in_hi):
        if pre_lo >= pre_hi:
            return None
        root_val = preorder[pre_lo]
        root = TreeNode(root_val)
        i = pos[root_val]
        left_size = i - in_lo
        root.left = build(pre_lo + 1, pre_lo + 1 + left_size, in_lo, i)
        root.right = build(pre_lo + 1 + left_size, pre_hi, i + 1, in_hi)
        return root
    return build(0, len(preorder), 0, len(inorder))
```

- 前序的第一个元素是根，在中序里找到它就能切出左右子树
- 哈希表把「找根位置」从 O(n) 降到 O(1)
- 易错：`left_size = i - in_lo`，不能直接用 `i`；右子树的中序从 `i + 1` 开始

### 108. 将有序数组转换为二叉搜索树 —— 形状六

```python
def sortedArrayToBST(nums):
    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = TreeNode(nums[mid])
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node
    return build(0, len(nums) - 1)
```

- 取中点当根，左右元素数量最多差 1，树自然平衡
- 和 105 对比，105 要查哈希表定位根，108 的根就是中点，直接算出来
- 易错：闭区间下空区间是 `lo > hi`，写成 `lo >= hi` 会漏掉单个元素；用切片写法空间会涨到 O(n log n)

## 十五题总表

| 题号 | 形状 | 时间 | 空间 |
| --- | --- | --- | --- |
| 226 翻转二叉树 | 一遍历，就地修改 | O(n) | O(h) |
| 114 展开为链表 | 一遍历，就地修改 | O(n) | O(1) |
| 94 中序遍历 | 二遍历，收集 | O(n) | O(h) |
| 102 层序遍历 | 二遍历，收集 | O(n) | O(w) |
| 199 右视图 | 二遍历，收集 | O(n) | O(w) |
| 230 第 K 小 | 二遍历，收集中途停 | O(h + k) | O(h) |
| 104 最大深度 | 三自底向上 | O(n) | O(h) |
| 101 对称二叉树 | 三自底向上，双树 | O(n) | O(h) |
| 236 最近公共祖先 | 三自底向上 | O(n) | O(h) |
| 543 直径 | 四自底向上加全局 | O(n) | O(h) |
| 124 最大路径和 | 四自底向上加全局 | O(n) | O(h) |
| 98 验证 BST | 五自顶向下 | O(n) | O(h) |
| 437 路径总和 III | 五自顶向下加哈希 | O(n) | O(h) |
| 105 前序中序构造 | 六分治构造 | O(n) | O(n) |
| 108 有序数组转 BST | 六分治构造 | O(n) | O(log n) |

`h` 是树高，`w` 是最大层宽。平衡树时 `h` 是 O(log n)，退化时是 O(n)。

## BST 的三条性质

第一，中序遍历严格递增。230 和 98 都建立在这条上。

第二，每个节点的值大于左子树里所有值，小于右子树里所有值。注意是整棵子树，看漏「所有」两个字就会写出只比较父子的错误代码。

第三，可以用取值范围描述约束，98 就是把区间一路往下传。

## 共同规律

树题只有两个变量。一个是「递归函数返回什么」，另一个是「信息往哪个方向流」。

- 信息从下往上收，用后序，接住返回值
- 信息从上往下带，用前序，把状态做成参数
- 只需要走一遍，前序后序都行，不需要返回值
- 在 BST 上按顺序处理，用中序

遇到拐弯的路径，比如 543 和 124，要记住那个拐弯值只用来更新全局答案，返回给上层的必须是能继续接的直路。

写之前先在纸上画两三个节点，把递归函数的含义写成一句中文。定义对了，代码自然就出来了。
