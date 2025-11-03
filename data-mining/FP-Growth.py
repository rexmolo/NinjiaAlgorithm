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
# 10. MINING PATTERNS: THE COMPLETE FP-GROWTH ALGORITHM
# ============================================================================

def get_conditional_pattern_base(root, item_name):
    """
    Get the conditional pattern base for an item.
    This is the collection of prefix paths ending with this item.
    
    Args:
        root: Root of the FP-Tree
        item_name: Item to find patterns for
    
    Returns:
        List of (prefix_path, count) tuples
    """
    # Find all nodes with this item
    nodes = collect_all_nodes(root, item_name)
    
    # Collect all prefix paths
    conditional_patterns = []
    
    for node in nodes:
        # Get the path from root to this node (excluding the node itself)
        path = []
        count = node.count
        current = node.parent
        
        while current.item_name != "Root":
            path.append(current.item_name)
            current = current.parent
        
        # Reverse to get root-to-node order
        path.reverse()
        
        if path:  # Only add if there's a prefix path
            conditional_patterns.append((path, count))
    
    return conditional_patterns


def build_conditional_fp_tree(conditional_patterns, min_support):
    """
    Build a conditional FP-Tree from conditional pattern base
    
    Args:
        conditional_patterns: List of (path, count) tuples
        min_support: Minimum support threshold
    
    Returns:
        Tuple of (root, frequent_items, item_order) or (None, None, None) if empty
    """
    # Count items in conditional patterns
    item_counts = Counter()
    for path, count in conditional_patterns:
        for item in path:
            item_counts[item] += count
    
    # Filter by min support
    frequent_items = {item: cnt 
                     for item, cnt in item_counts.items() 
                     if cnt >= min_support}
    
    if not frequent_items:
        return None, None, None
    
    # Get frequency order
    item_order = get_sorted_frequent_items(frequent_items)
    
    # Build conditional tree
    root = FPNode("Root", 0, None)
    
    for path, count in conditional_patterns:
        # Filter and reorder
        ordered = reorder_transaction(path, item_order)
        if ordered:
            insert_transaction(root, ordered, count)
    
    return root, frequent_items, item_order


def mine_fp_tree(root, min_support, prefix=[], frequent_patterns=None):
    """
    Recursively mine frequent patterns from FP-Tree
    
    Args:
        root: Root of the FP-Tree
        min_support: Minimum support threshold
        prefix: Current prefix pattern being built
        frequent_patterns: Dictionary to store {pattern: support}
    
    Returns:
        Dictionary of {pattern: support}
    """
    if frequent_patterns is None:
        frequent_patterns = {}
    
    # Get all items in this tree (from leaf to root order - least frequent first)
    items = {}
    
    def collect_items(node):
        if node.item_name != "Root":
            if node.item_name not in items:
                items[node.item_name] = 0
            items[node.item_name] += node.count
        for child in node.children.values():
            collect_items(child)
    
    collect_items(root)
    
    # Sort items by frequency (ascending - mine least frequent first)
    sorted_items = sorted(items.items(), key=lambda x: x[1])
    
    # Mine each item
    for item, support in sorted_items:
        # Create new pattern by adding this item to prefix
        new_pattern = prefix + [item]
        
        # Store this frequent pattern
        pattern_key = tuple(sorted(new_pattern))
        if pattern_key not in frequent_patterns or frequent_patterns[pattern_key] < support:
            frequent_patterns[pattern_key] = support
        
        # Get conditional pattern base for this item
        conditional_patterns = get_conditional_pattern_base(root, item)
        
        # Build conditional FP-Tree
        cond_root, cond_items, cond_order = build_conditional_fp_tree(
            conditional_patterns, min_support
        )
        
        # If conditional tree is not empty, mine it recursively
        if cond_root is not None:
            mine_fp_tree(cond_root, min_support, new_pattern, frequent_patterns)
    
    return frequent_patterns


def print_frequent_patterns(patterns, transactions):
    """
    Print frequent patterns in a nice format
    
    Args:
        patterns: Dictionary of {pattern: support}
        transactions: Original transactions for calculating percentage
    """
    print("\n" + "=" * 70)
    print("ALL FREQUENT PATTERNS (Itemsets)")
    print("=" * 70)
    
    # Group by size
    by_size = {}
    for pattern, support in patterns.items():
        size = len(pattern)
        if size not in by_size:
            by_size[size] = []
        by_size[size].append((pattern, support))
    
    # Print by size
    total_count = len(transactions)
    
    for size in sorted(by_size.keys()):
        print(f"\n{size}-itemsets:")
        print("-" * 70)
        
        # Sort by support (descending)
        by_size[size].sort(key=lambda x: (-x[1], x[0]))
        
        for pattern, support in by_size[size]:
            percent = (support / total_count) * 100
            items_str = ", ".join(pattern)
            print(f"  {{{items_str}}}")
            print(f"    Support: {support}/{total_count} transactions ({percent:.1f}%)")


def demonstrate_mining_process(root, item_name, min_support):
    """
    Demonstrate the mining process step-by-step for one item
    
    Args:
        root: Root of FP-Tree
        item_name: Item to demonstrate mining for
        min_support: Minimum support threshold
    """
    print("\n" + "=" * 70)
    print(f"DETAILED MINING EXAMPLE: {item_name}")
    print("=" * 70)
    
    # Step 1: Get conditional pattern base
    print(f"\n[Step 1] Find all occurrences of '{item_name}' in the tree:")
    nodes = collect_all_nodes(root, item_name)
    print(f"  Found {len(nodes)} node(s)")
    
    print(f"\n[Step 2] Extract prefix paths (Conditional Pattern Base):")
    conditional_patterns = get_conditional_pattern_base(root, item_name)
    
    total_support = 0
    for path, count in conditional_patterns:
        print(f"  {path} : {count}")
        total_support += count
    
    print(f"\n  → Total support for '{item_name}': {total_support}")
    
    # Step 2: Build conditional FP-Tree
    print(f"\n[Step 3] Build Conditional FP-Tree for '{item_name}':")
    cond_root, cond_items, cond_order = build_conditional_fp_tree(
        conditional_patterns, min_support
    )
    
    if cond_root is None:
        print(f"  → No frequent items co-occur with '{item_name}'")
        print(f"  → This means '{item_name}' is often bought alone or with infrequent items")
    else:
        print(f"  → Frequent items that co-occur with '{item_name}': {cond_items}")
        print(f"  → Conditional FP-Tree structure:")
        print_tree(cond_root, "    ", True, cond_order)
        
        # Mine patterns
        print(f"\n[Step 4] Mine patterns from conditional tree:")
        patterns = mine_fp_tree(cond_root, min_support, [item_name], {})
        
        for pattern, support in sorted(patterns.items(), key=lambda x: -x[1]):
            print(f"  {set(pattern)} : {support}")


# ============================================================================
# 11. MAIN EXECUTION
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
    
    # ========================================================================
    # NOW THE REAL MAGIC: MINING PATTERNS FROM THE TREE
    # ========================================================================
    
    # Demonstrate mining for Laptop_Bag step-by-step
    demonstrate_mining_process(root, "Laptop_Bag", min_support)
    
    # Demonstrate mining for USB_Cable
    demonstrate_mining_process(root, "USB_Cable", min_support)
    
    # Mine ALL frequent patterns
    print("\n" + "=" * 70)
    print("MINING ALL FREQUENT PATTERNS")
    print("=" * 70)
    print("\nThis is where FP-Growth shows its power!")
    print("We'll now extract ALL frequent itemsets in one pass...")
    
    all_patterns = mine_fp_tree(root, min_support)
    
    # Print all patterns
    print_frequent_patterns(all_patterns, transactions)
    
    # Business insights
    print("\n" + "=" * 70)
    print("BUSINESS INSIGHTS & RECOMMENDATIONS")
    print("=" * 70)
    
    print("\n📦 PRODUCT BUNDLES TO CREATE:")
    # Find 2-itemsets with high support
    two_itemsets = [(p, s) for p, s in all_patterns.items() if len(p) == 2]
    two_itemsets.sort(key=lambda x: -x[1])
    
    for pattern, support in two_itemsets[:3]:
        percent = (support / len(transactions)) * 100
        print(f"  • Bundle: {' + '.join(pattern)}")
        print(f"    Reason: Bought together in {support}/{len(transactions)} orders ({percent:.1f}%)")
    
    print("\n🎯 RECOMMENDATION ENGINE RULES:")
    # Find 2-itemsets for recommendations
    for pattern, support in two_itemsets[:3]:
        items = list(pattern)
        print(f"  • 'Customers who bought {items[0]} also bought {items[1]}'")
    
    print("\n📊 INVENTORY MANAGEMENT:")
    print("  • High-demand items (stock up): Mouse, Laptop, Keyboard")
    print("  • Bundle items (store nearby): Mouse + Keyboard, Laptop + Laptop_Bag")
    print("  • Low-demand items (reduce stock): Screen_Protector")
    
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS: WHY FP-GROWTH WINS")
    print("=" * 70)
    print("\n✅ Database Scans: Only 2 (vs Apriori's multiple scans)")
    print("✅ Candidate Generation: ZERO (vs Apriori's exponential candidates)")
    print("✅ Memory Efficiency: Tree compresses repeated patterns")
    print("✅ Speed: Mines patterns directly from tree structure")
    print("\nFor this small dataset, the difference isn't huge.")
    print("But with 10,000+ products and 1M+ transactions?")
    print("FP-Growth is 10-100x faster than Apriori! 🚀")
    print("=" * 70)


if __name__ == "__main__":
    main()