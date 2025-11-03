"""
Apriori Algorithm Implementation for E-commerce Order Data
Each function does ONE specific thing - easy to understand and test!
"""

from itertools import combinations
from collections import defaultdict


# ============================================================================
# STEP 1: DATA PREPARATION FUNCTIONS
# ============================================================================

def load_transactions():
    """
    Load our e-commerce transaction data.
    Returns: List of transactions (each transaction is a set of items)
    """
    transactions = [
        {'Bread', 'Milk'},                    # T1
        {'Bread', 'Butter', 'Milk'},          # T2
        {'Bread', 'Butter'},                  # T3
        {'Milk', 'Butter'},                   # T4
        {'Bread', 'Milk', 'Butter'}           # T5
    ]
    return transactions


# ============================================================================
# STEP 2: SUPPORT CALCULATION FUNCTIONS
# ============================================================================

def calculate_support(itemset, transactions):
    """
    Calculate support for a single itemset.
    
    Args:
        itemset: A frozenset of items (e.g., frozenset({'Bread', 'Milk'}))
        transactions: List of transaction sets
    
    Returns:
        Support value (float between 0 and 1)
    """
    count = 0
    for transaction in transactions:
        # Check if itemset is a subset of transaction
        if itemset.issubset(transaction):
            count += 1
    
    support = count / len(transactions)
    return support


def get_support_for_all_itemsets(itemsets, transactions):
    """
    Calculate support for multiple itemsets at once.
    
    Args:
        itemsets: List of frozensets
        transactions: List of transaction sets
    
    Returns:
        Dictionary: {itemset: support_value}
    """
    support_dict = {}
    for itemset in itemsets:
        support_dict[itemset] = calculate_support(itemset, transactions)
    return support_dict


# ============================================================================
# STEP 3: FILTERING FUNCTIONS
# ============================================================================

def filter_by_min_support(itemset_support_dict, min_support):
    """
    Filter itemsets that meet minimum support threshold.
    
    Args:
        itemset_support_dict: Dictionary of {itemset: support}
        min_support: Minimum support threshold (e.g., 0.6 for 60%)
    
    Returns:
        Dictionary of frequent itemsets that meet threshold
    """
    frequent_itemsets = {}
    for itemset, support in itemset_support_dict.items():
        if support >= min_support:
            frequent_itemsets[itemset] = support
    
    return frequent_itemsets


# ============================================================================
# STEP 4: CANDIDATE GENERATION FUNCTIONS
# ============================================================================

def get_unique_items(transactions):
    """
    Extract all unique items from transactions.
    
    Returns:
        Set of all unique items
    """
    unique_items = set()
    for transaction in transactions:
        unique_items.update(transaction)
    return unique_items


def generate_1_itemsets(transactions):
    """
    Generate all 1-itemsets (individual items).
    
    Returns:
        List of frozensets, each containing one item
    """
    unique_items = get_unique_items(transactions)
    itemsets = [frozenset([item]) for item in unique_items]
    return itemsets


def generate_next_candidates(frequent_itemsets, k):
    """
    Generate candidate k-itemsets from frequent (k-1)-itemsets.
    This is the SMART part of Apriori!
    
    Args:
        frequent_itemsets: Dictionary of frequent (k-1)-itemsets
        k: Size of itemsets to generate
    
    Returns:
        List of candidate k-itemsets (frozensets)
    """
    items = set()
    # Extract all items from frequent itemsets
    for itemset in frequent_itemsets.keys():
        items.update(itemset)
    
    # Generate all possible k-combinations
    candidates = []
    for combination in combinations(sorted(items), k):
        candidate = frozenset(combination)
        
        # APRIORI PRINCIPLE: Check if all (k-1) subsets are frequent
        if has_infrequent_subset(candidate, frequent_itemsets):
            continue  # Skip this candidate
        
        candidates.append(candidate)
    
    return candidates


def has_infrequent_subset(candidate, frequent_itemsets):
    """
    Check if candidate has any (k-1) subset that is NOT frequent.
    
    This implements the Apriori Principle pruning!
    
    Args:
        candidate: A k-itemset to check
        frequent_itemsets: Dictionary of frequent (k-1)-itemsets
    
    Returns:
        True if has infrequent subset, False otherwise
    """
    k = len(candidate)
    # Generate all (k-1) subsets
    for subset in combinations(candidate, k - 1):
        if frozenset(subset) not in frequent_itemsets:
            return True  # Found an infrequent subset!
    return False


# ============================================================================
# STEP 5: MAIN APRIORI ALGORITHM
# ============================================================================

def apriori(transactions, min_support):
    """
    Main Apriori algorithm.
    
    Args:
        transactions: List of transaction sets
        min_support: Minimum support threshold (0.0 to 1.0)
    
    Returns:
        Dictionary of all frequent itemsets at all levels
    """
    print(f"Running Apriori with min_support = {min_support:.0%}\n")
    print(f"Total transactions: {len(transactions)}\n")
    print("=" * 70)
    
    all_frequent_itemsets = {}
    k = 1
    
    # STEP 1: Generate and filter 1-itemsets
    print(f"\n### FINDING FREQUENT {k}-ITEMSETS ###")
    candidates = generate_1_itemsets(transactions)
    print(f"Generated {len(candidates)} candidate 1-itemsets")
    
    support_dict = get_support_for_all_itemsets(candidates, transactions)
    frequent_itemsets = filter_by_min_support(support_dict, min_support)
    
    print(f"Found {len(frequent_itemsets)} frequent 1-itemsets:")
    display_itemsets(frequent_itemsets)
    
    all_frequent_itemsets.update(frequent_itemsets)
    
    # STEP 2: Iteratively generate larger itemsets
    k = 2
    while frequent_itemsets:
        print(f"\n### FINDING FREQUENT {k}-ITEMSETS ###")
        
        # Generate candidates from previous frequent itemsets
        candidates = generate_next_candidates(frequent_itemsets, k)
        
        if not candidates:
            print(f"No candidates generated. Stopping.")
            break
        
        print(f"Generated {len(candidates)} candidate {k}-itemsets")
        
        # Calculate support and filter
        support_dict = get_support_for_all_itemsets(candidates, transactions)
        frequent_itemsets = filter_by_min_support(support_dict, min_support)
        
        if frequent_itemsets:
            print(f"Found {len(frequent_itemsets)} frequent {k}-itemsets:")
            display_itemsets(frequent_itemsets)
            all_frequent_itemsets.update(frequent_itemsets)
        else:
            print(f"No frequent {k}-itemsets found. Stopping.")
            print(f"\n💡 Why we stop: If {k}-itemsets aren't frequent,")
            print(f"   any {k+1}-itemsets containing them can't be frequent either!")
            break
        
        k += 1
    
    return all_frequent_itemsets


# ============================================================================
# STEP 6: DISPLAY FUNCTIONS
# ============================================================================

def display_itemsets(itemset_support_dict):
    """Pretty print itemsets with their support."""
    for itemset, support in sorted(itemset_support_dict.items(), 
                                   key=lambda x: x[1], reverse=True):
        items = ', '.join(sorted(itemset))
        print(f"  {{{items}}}: {support:.1%} support")


def display_transactions(transactions):
    """Display all transactions in a readable format."""
    print("\n### TRANSACTION DATABASE ###")
    for i, transaction in enumerate(transactions, 1):
        items = ', '.join(sorted(transaction))
        print(f"  T{i}: {{{items}}}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Load data
    transactions = load_transactions()
    display_transactions(transactions)
    
    # Run Apriori with 60% minimum support
    min_support = 0.6  # 60%
    
    print("\n" + "=" * 70)
    frequent_itemsets = apriori(transactions, min_support)
    
    # Final summary
    print("\n" + "=" * 70)
    print(f"\n### FINAL RESULTS ###")
    print(f"Found {len(frequent_itemsets)} total frequent itemsets:")
    display_itemsets(frequent_itemsets)