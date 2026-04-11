"""
merge_vendor_contacts.py

Reads Unapplied_Vendors.csv, collapses duplicate Vendor Number rows by:
  - merging and deduplicating all Vendor Contacts (semicolon-delimited emails)
  - selecting Owner using a global rank: the owner who covers the most distinct
    Vendor Numbers across the entire file wins; ties broken by first appearance

Writes the result to Unapplied_Vendors_Merged.csv in the same directory.
"""

import os
import pandas as pd

INPUT_FILE = os.path.join(os.path.dirname(__file__), "Unapplied_Vendors.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "Unapplied_Vendors_Merged.csv")


def merge_contacts(contact_series: pd.Series) -> str:
    """
    Merge all semicolon-delimited contact strings in a group into one
    deduplicated, semicolon-delimited string.

    Args:
        contact_series: Series of contact strings, each potentially containing
                        multiple semicolon-separated email addresses.

    Returns:
        Single string of unique email addresses joined by ";", preserving
        first-seen order.
    """
    seen: dict[str, None] = {}
    for cell in contact_series.dropna():
        for email in cell.split(";"):
            email = email.strip()
            if email:
                seen[email] = None  # dict preserves insertion order (Python 3.7+)
    return ";".join(seen.keys())


def pick_owner(owner_series: pd.Series, global_rank: dict[str, int]) -> str:
    """
    Select the best owner for a vendor number group using the global rank.

    The global rank scores each owner by how many distinct Vendor Numbers they
    appear against in the full file (higher = broader coverage). Among owners
    present in this group, the highest-ranked wins. Ties are broken by first
    appearance in the group (i.e., earliest row in the original file).

    Args:
        owner_series: Series of Owner values for this vendor number group,
                      in original file order.
        global_rank:  Mapping of owner -> distinct-vendor-number count across
                      the entire file.

    Returns:
        The selected owner string.
    """
    # Iterate in original order so the first occurrence wins any tie naturally.
    best_owner = None
    best_score = -1
    for owner in owner_series:
        score = global_rank.get(owner, 0)
        if score > best_score:
            best_score = score
            best_owner = owner
    return best_owner


def main() -> None:
    """
    Load the input CSV, merge contacts and resolve owners per Vendor Number,
    and write the deduplicated result to the output file.
    """
    df = pd.read_csv(INPUT_FILE, dtype=str)
    print(f"Input rows : {len(df)}")
    print(f"Unique vendor numbers (input): {df['Vendor Number'].nunique()}")

    # Build global owner rank: count of distinct Vendor Numbers per owner.
    # groupby preserves first-appearance order within ties when we later iterate.
    global_rank = (
        df.groupby("Owner")["Vendor Number"]
        .nunique()
        .to_dict()
    )

    rows = []
    for vendor_number, group in df.groupby("Vendor Number", sort=False):
        rows.append({
            "Owner": pick_owner(group["Owner"], global_rank),
            "Vendor Number": vendor_number,
            "Vendor Contacts": merge_contacts(group["Vendor Contacts"]),
        })

    result = pd.DataFrame(rows, columns=["Owner", "Vendor Number", "Vendor Contacts"])
    result.to_csv(OUTPUT_FILE, index=False)

    print(f"Output rows: {len(result)}")
    print(f"Written to : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
