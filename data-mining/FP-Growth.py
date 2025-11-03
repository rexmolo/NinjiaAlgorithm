
"""
FP-Growth Algorithm Implementation for E-Commerce Order Analysis
TechGear Online Store Example - Finding Frequent Product Combinations
"""

from collections import defaultdict, Counter


# ============================================================================
# 1. DATA STRUCTURES
# ============================================================================

class FPNode:
    """
    A node in the FP-Tree.
    Each node represents an item and stores:
    - item_name: the product name
    - count: how many transactions pass through this node
    - parent: link to parent node
    - children: dictionary of child nodes
    - node_link: link to next node with same item (for header table)
    """
    def __init__(self, item_name, count, parent):
        self.item_name = item_name
        self.count = count
        self.parent = parent
        self.children = {}  # {item_name: FPNode}
        self.node_link = None  # Link to next node with same item
    
    def increment(self, count):
        """Increase the count when another transaction passes through"""
        self.count += count


# ============================================================================
# 2. STEP 1: SCAN DATABASE AND COUNT ITEM FREQUENCIES
# ============================================================================

def scan_and_count_items(transactions):
    """
    First database scan: Count how many times each item appears
    
    Args:
        transactions: List of transactions, where each transaction is a list of items
    
    Returns:
        Counter object with item frequencies
    """
    item_counts = Counter()
    
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    
    return item_counts


# ============================================================================
# 3. STEP 2: FILTER ITEMS BY MINIMUM SUPPORT
# ============================================================================

def filter_by_min_support(item_counts, min_support):
    """
    Keep only items that meet minimum support threshold
    
    Args:
        item_counts: Counter with item frequencies
        min_support: Minimum number of transactions an item must appear in
    
    Returns:
        Dictionary of {item: count} for frequent items
    """
    frequent_items = {item: count 
                     for item, count in item_counts.items() 
                     if count >= min_support}
    
    return frequent_items


# ============================================================================
# 4. STEP 3: CREATE FREQUENCY-ORDERED LIST
# ============================================================================

def get_sorted_frequent_items(frequent_items):
    """
    Sort items by frequency (descending order)
    Items with same frequency are sorted alphabetically for consistency
    
    Args:
        frequent_items: Dictionary of {item: count}
    
    Returns:
        List of items sorted by frequency (highest first)
    """
    # Sort by count (descending), then by name (ascending) for ties
    sorted_items = sorted(frequent_items.items(), 
                         key=lambda x: (-x[1], x[0]))
    
    return [item for item, count in sorted_items]


# ============================================================================
# 5. STEP 4: REORDER TRANSACTION BY FREQUENCY
# ============================================================================

def reorder_transaction(transaction, item_order):
    """
    Remove infrequent items and sort remaining items by global frequency
    
    Args:
        transaction: List of items in a transaction
        item_order: List of frequent items in frequency order
    
    Returns:
        List of items sorted by frequency order
    """
    # Create position map for quick lookup
    order_map = {item: idx for idx, item in enumerate(item_order)}
    
    # Keep only frequent items
    filtered = [item for item in transaction if item in order_map]
    
    # Sort by frequency order
    filtered.sort(key=lambda x: order_map[x])
    
    return filtered


# ============================================================================
# 6. STEP 5: INSERT TRANSACTION INTO FP-TREE
# ============================================================================

def insert_transaction(root, transaction, count=1):
    """
    Insert a transaction into the FP-Tree
    
    Args:
        root: Root node of the FP-Tree
        transaction: Ordered list of items
        count: How many times to count this transaction (default 1)
    """
    current_node = root
    
    for item in transaction:
        # Check if child already exists
        if item in current_node.children:
            # Increment existing node's count
            current_node.children[item].increment(count)
        else:
            # Create new child node
            new_node = FPNode(item, count, current_node)
            current_node.children[item] = new_node
        
        # Move to child node
        current_node = current_node.children[item]


# ============================================================================
# 7. STEP 6: BUILD COMPLETE FP-TREE
# ============================================================================

def build_fp_tree(transactions, min_support):
    """
    Main function to build the FP-Tree
    
    Args:
        transactions: List of transactions
        min_support: Minimum support threshold
    
    Returns:
        Tuple of (root_node, frequent_items_dict, item_order_list)
    """
    print("=" * 70)
    print("BUILDING FP-TREE")
    print("=" * 70)
    
    # Step 1: First scan - count items
    print("\n[1] First Database Scan: Counting item frequencies...")
    item_counts = scan_and_count_items(transactions)
    print(f"    Item counts: {dict(item_counts)}")
    
    # Step 2: Filter by minimum support
    print(f"\n[2] Filtering items with support < {min_support}...")
    frequent_items = filter_by_min_support(item_counts, min_support)
    print(f"    Frequent items: {frequent_items}")
    
    # Step 3: Sort by frequency
    print("\n[3] Sorting items by frequency (descending)...")
    item_order = get_sorted_frequent_items(frequent_items)
    print(f"    Frequency order: {item_order}")
    
    # Step 4 & 5: Second scan - build tree
    print("\n[4] Second Database Scan: Building FP-Tree...")
    root = FPNode("Root", 0, None)
    
    for idx, transaction in enumerate(transactions, 1):
        # Reorder transaction
        ordered = reorder_transaction(transaction, item_order)
        if ordered:  # Only insert if transaction has frequent items
            print(f"    T{idx:03d}: {transaction} → {ordered}")
            insert_transaction(root, ordered)
    
    print("\n[5] FP-Tree construction complete!")
    
    return root, frequent_items, item_order


# ============================================================================
# 8. VISUALIZATION: PRINT THE TREE
# ============================================================================

def print_tree(node, prefix="", is_last=True, item_order=None):
    """
    Print the FP-Tree in a visual tree structure
    
    Args:
        node: Current node to print
        prefix: Prefix string for tree branches
        is_last: Whether this is the last child
        item_order: Optional list to sort children by frequency order
    """
    # Print current node
    if node.item_name != "Root":
        connector = "└─ " if is_last else "├─ "
        print(f"{prefix}{connector}{node.item_name}:{node.count}")
        prefix += "   " if is_last else "│  "
    
    # Get children
    children = list(node.children.values())
    
    # Sort children by frequency order if provided
    if item_order and children:
        order_map = {item: idx for idx, item in enumerate(item_order)}
        children.sort(key=lambda x: order_map.get(x.item_name, 999))
    
    # Print children
    for i, child in enumerate(children):
        is_last_child = (i == len(children) - 1)
        print_tree(child, prefix, is_last_child, item_order)


# ============================================================================
# 9. ANALYSIS: EXTRACT PATTERNS FROM THE TREE
# ============================================================================

def find_prefix_paths(node):
    """
    Find all prefix paths for a given node
    (paths from root to this node, excluding the node itself)
    
    Args:
        node: The FPNode to find prefix paths for
    
    Returns:
        List of (path, count) tuples
    """
    paths = []
    
    # Traverse up to root
    path = []
    current = node.parent
    
    while current.item_name != "Root":
        path.append(current.item_name)
        current = current.parent
    
    # Reverse to get root-to-node order
    path.reverse()
    
    if path:  # Only add if there's a path
        paths.append((path, node.count))
    
    return paths


def collect_all_nodes(root, item_name):
    """
    Collect all nodes with a specific item name in the tree
    
    Args:
        root: Root of the FP-Tree
        item_name: Item to search for
    
    Returns:
        List of FPNode objects with that item name
    """
    nodes = []
    
    def traverse(node):
        if node.item_name == item_name:
            nodes.append(node)
        for child in node.children.values():
            traverse(child)
    
    traverse(root)
    return nodes


def mine_single_path(root, prefix, min_support):
    """
    Mine patterns from a single-path tree (optimization)
    
    Args:
        root: Root of single-path tree
        prefix: Current prefix pattern
        min_support: Minimum support threshold
    
    Returns:
        List of (pattern, support) tuples
    """
    patterns = []
    current = root
    path_items = []
    
    # Collect all items in the single path
    while current.children:
        child = list(current.children.values())[0]
        path_items.append((child.item_name, child.count))
        current = child
    
    # Generate all combinations of the path
    n = len(path_items)
    for i in range(1, 2**n):
        pattern = list(prefix)
        min_count = float('inf')
        
        for j in range(n):
            if i & (1 << j):
                pattern.append(path_items[j][0])
                min_count = min(min_count, path_items[j][1])
        
        if min_count >= min_support:
            patterns.append((tuple(sorted(pattern)), min_count))
    
    return patterns


# ============================================================================
# 10. MAIN EXECUTION
# ============================================================================

def main():
    # Our TechGear e-commerce transactions
    transactions = [
        ["Laptop", "Mouse", "USB_Cable", "Laptop_Bag"],              # T001 - Alice
        ["Mouse", "Keyboard", "USB_Cable"],                          # T002 - Bob
        ["Laptop", "Mouse", "Laptop_Bag", "Screen_Protector"],       # T003 - Carol
        ["Mouse", "Keyboard"],                                       # T004 - Dave
        ["Laptop", "Mouse", "USB_Cable", "Keyboard", "Laptop_Bag"],  # T005 - Emma
        ["Mouse", "USB_Cable"],                                      # T006 - Frank
        ["Laptop", "Keyboard", "Laptop_Bag"],                        # T007 - Grace
        ["Mouse", "Keyboard", "USB_Cable"],                          # T008 - Henry
        ["Laptop", "Mouse", "Laptop_Bag"],                           # T009 - Iris
    ]
    
    customer_names = ["Alice", "Bob", "Carol", "Dave", "Emma", 
                     "Frank", "Grace", "Henry", "Iris"]
    
    # Minimum support: 40% of 9 transactions = 4 transactions
    min_support = 4
    min_support_percent = (min_support / len(transactions)) * 100
    
    print("\n" + "=" * 70)
    print("FP-GROWTH ALGORITHM - TECHGEAR E-COMMERCE ANALYSIS")
    print("=" * 70)
    print(f"\nDataset: {len(transactions)} transactions")
    print(f"Minimum Support: {min_support} transactions ({min_support_percent:.0f}%)")
    print("\nOriginal Transactions:")
    print("-" * 70)
    for i, (customer, transaction) in enumerate(zip(customer_names, transactions), 1):
        print(f"T{i:03d} ({customer:6s}): {transaction}")
    
    # Build FP-Tree
    root, frequent_items, item_order = build_fp_tree(transactions, min_support)
    
    # Visualize the tree
    print("\n" + "=" * 70)
    print("FP-TREE STRUCTURE")
    print("=" * 70)
    print_tree(root, item_order=item_order)
    
    # Analyze patterns for one item as example
    print("\n" + "=" * 70)
    print("PATTERN ANALYSIS EXAMPLE: USB_Cable")
    print("=" * 70)
    
    # Find all nodes containing USB_Cable
    usb_nodes = collect_all_nodes(root, "USB_Cable")
    print(f"\nFound {len(usb_nodes)} node(s) containing 'USB_Cable' in the tree")
    
    # Extract prefix paths
    print("\nPrefix paths (what items were purchased BEFORE USB_Cable):")
    all_prefix_paths = []
    for node in usb_nodes:
        paths = find_prefix_paths(node)
        all_prefix_paths.extend(paths)
        for path, count in paths:
            print(f"  {path} : {count} times")
    
    if all_prefix_paths:
        print("\n→ This tells us: USB_Cable is often bought with Mouse and Keyboard!")
        print("→ Business insight: Bundle these items or recommend them together")
    
    print("\n" + "=" * 70)
    print("QUESTIONS TO EXPLORE:")
    print("=" * 70)
    print("1. Trace the path 'Mouse → Laptop → Laptop_Bag:4'")
    print("   - Which transactions created this path?")
    print("   - Why is the count 4?")
    print("\n2. Why is there a separate 'Keyboard:1' branch from Root?")
    print("   - Which transaction created it?")
    print("   - Why doesn't it start with Mouse?")
    print("\n3. Compare this to Apriori:")
    print("   - How many database scans did FP-Growth use? (Answer: 2)")
    print("   - Did we generate any candidate itemsets? (Answer: No!)")
    print("   - All patterns are encoded in this compact tree structure!")
    print("=" * 70)


if __name__ == "__main__":
    main()