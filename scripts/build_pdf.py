"""
build_heinsius_pdf.py
=====================
Downloads all per-page PDFs for the Briefwisseling Heinsius from the Huygens
server, merges them in order, and injects a full hierarchical PDF bookmark
outline (sidebar Table of Contents).

Usage
-----
    pip install pypdf requests
    python build_heinsius_pdf.py

The script expects heinsius_01_GS158_by_page.csv to be in the same directory.
Output: heinsius_01_GS158_COMPLETE.pdf

Structure of the bookmark outline produced
-------------------------------------------
FrontMatter (flat)
    I   [title from level_0_heading if present, else file_number]
    II  ...
    ...
Inleiding                               ← level 0, first page where it appears
Briefwisseling                          ← level 0
    1  van Albemarle, 18 maart 1702.    ← level 1, one entry per letter number
    2  van Marlborough, 19 maart 1702.
    ...
Lijst van gebruikte afkortingen         ← BackMatter level 0 sections
Overzicht van de vindplaatsen ...
...

with Image.open("tiff/heinsius_01_GS158_662.tif") as img:
    # Converts the tiff to rgb
    img = img.convert("RGB")
    img.save("output.pdf", "PDF")
"""

import os
import re
# import sys
# import time
# import requests
import pandas as pd
# from pathlib import Path
from pypdf import PdfWriter, PdfReader
from PIL import Image

# ── Configuration ────────────────────────────────────────────────────────────

workspace = os.getenv("GITHUB_WORKSPACE", "../")
GROUP = "retro"
SERIES = "heinsius"
BOOK = "heinsius_01_GS158"

# CSV_FILE   = "heinsius_01_GS158_by_page.csv"
CSV_FILE = os.path.join(workspace, "{}/{}/{}/dataset/csv/{}_by_page.csv".format(GROUP,SERIES,BOOK,BOOK))
OUTPUT_PRODUCTS = os.path.join(workspace, "{}/{}/{}/products".format(GROUP,SERIES,BOOK))
OUTPUT_PDF = os.path.join(OUTPUT_PRODUCTS,"{}.pdf".format(BOOK))
CACHE_DIR  = os.path.join(workspace, "pdf_cache")  # created pdf pages are cached here
IMAGE_DIR = os.path.join(workspace, "{}/{}/{}/tiff".format(GROUP,SERIES,BOOK))
# DELAY      = 0.3                        # seconds between requests (be polite)

# ── Roman numeral sort helper ─────────────────────────────────────────────────

ROMAN = {"I":1,"V":5,"X":10,"L":50,"C":100,"D":500,"M":1000}

def roman_to_int(s: str) -> int:
    """Convert a Roman numeral string to an integer (for sorting)."""
    s = s.upper().strip()
    result, prev = 0, 0
    for ch in reversed(s):
        val = ROMAN.get(ch, 0)
        if val < prev:
            result -= val
        else:
            result += val
        prev = val
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)
    if not os.path.exists(OUTPUT_PRODUCTS):
        os.mkdir(OUTPUT_PRODUCTS)

    # 1. Load CSV
    print("Loading CSV …")
    df = pd.read_csv(CSV_FILE)
    print(f"  {len(df)} rows loaded")

    # 2. Create all PDFs (in CSV order = document order)
    print(f"\nCreating PDFs to '{CACHE_DIR}/' …")
    failed = []
    local_paths = []
    
    for _, row in df.iterrows():
        # url = row["pdf_url"]
        filebasename = row["filebasename"]
        # dest  = CACHE_DIR / fname
        with Image.open("{}/{}.tif".format(IMAGE_DIR,filebasename)) as img:
            # Converts the tiff to rgb
            img = img.convert("RGB")
            img.save("{}/{}.pdf".format(CACHE_DIR,filebasename), "PDF")
            local_paths.append("{}/{}.pdf".format(CACHE_DIR,filebasename))
        

    df["local_path"] = local_paths

    if failed:
        print(f"\n  ⚠  {len(failed)} downloads failed – they will be skipped.")

    # 3. Merge PDFs and track physical page numbers (0-based)
    print("\nMerging pages …")
    writer = PdfWriter()
    df["phys_page"] = -1          # physical 0-based page index in merged PDF

    for i, (idx, row) in enumerate(df.iterrows()):
        path = row["local_path"]
        if path is None:
            continue
        try:
            reader = PdfReader(str(path))
            phys   = len(writer.pages)
            df.at[idx, "phys_page"] = phys
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            print(f"  ✗ Could not read {path}: {e}")

        if (i + 1) % 100 == 0:
            print(f"  … merged {i+1}/{len(df)} pages")

    print(f"  Total pages in merged PDF: {len(writer.pages)}")
    # os.remove(CACHE_DIR)
    # 4. Build bookmark outline
    #
    # Strategy:
    #   • FrontMatter rows  → top-level bookmarks (roman-numeral pages)
    #   • First page where level_0_heading changes → top-level bookmark
    #   • Each letter (item_number + title, possibly multiple per row) → child
    #     under its level_0 parent
    #   • BackMatter sections → top-level bookmarks

    print("\nBuilding bookmark outline …")

    # Helper: get first valid phys_page for a group of rows
    def first_phys(rows):
        pages = rows[rows["phys_page"] >= 0]["phys_page"]
        return int(pages.iloc[0]) if len(pages) else None

    # ── 4a. FrontMatter group (single top-level bookmark + children per page)
    front = df[df["matter_type"] == "FrontMatter"].copy()
    if len(front):
        front_phys = first_phys(front)
        front_parent = writer.add_outline_item("Voorwerk", front_phys)
        for _, row in front.iterrows():
            p = row["phys_page"]
            if p < 0:
                continue
            fn   = str(row["file_number"])
            h0   = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
            # Use a clean heading if available, else just the roman numeral
            label = h0 if h0 and h0 not in ("nan", "no_value") else fn
            # Truncate very long HTML-ish labels
            label = re.sub(r"<[^>]+>", " ", label).strip()
            label = label[:80]
            writer.add_outline_item(f"{fn}  {label}" if label != fn else fn,
                                    p, parent=front_parent)

    # ── 4b. Build letter lookup: item_number → (phys_page, title_string)
    #    Rows can carry multiple letters separated by ";"
    letter_entries: list[tuple[int, str, int]] = []  # (letter_num_int, label, phys_page)

    for _, row in df[df["matter_type"] == "BodyMatter"].iterrows():
        p = row["phys_page"]
        if p < 0:
            continue
        if pd.isna(row["item_number"]):
            continue
        nums   = [s.strip() for s in str(row["item_number"]).split(";")]
        titles = [s.strip() for s in str(row["title"]).split(";")] if pd.notna(row["title"]) else []
        for j, num in enumerate(nums):
            try:
                n = int(num)
            except ValueError:
                continue
            t = titles[j] if j < len(titles) else ""
            letter_entries.append((n, t, p))

    # De-duplicate: keep first occurrence of each letter number
    seen_letters: set[int] = set()
    unique_letters: list[tuple[int, str, int]] = []
    for n, t, p in sorted(letter_entries, key=lambda x: x[0]):
        if n not in seen_letters:
            seen_letters.add(n)
            unique_letters.append((n, t, p))

    # ── 4c. level_0 sections (BodyMatter) – only "Briefwisseling" expected,
    #    but we handle any future section generically
    body = df[df["matter_type"] == "BodyMatter"].copy()
    body_sections = []
    prev_h0 = None
    for _, row in body.iterrows():
        h0 = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
        if h0 and h0 != prev_h0:
            p = row["phys_page"]
            if p >= 0:
                body_sections.append((h0, p))
            prev_h0 = h0

    # Add level_0 from FrontMatter that is NOT the generic voorwerk pages
    # (i.e., the "Inleiding" section which lives in FrontMatter rows with heading set)
    front_sections = []
    prev_h0 = None
    for _, row in front.iterrows():
        h0 = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
        if h0 and h0 not in ("nan", "no_value") and h0 != prev_h0:
            p = row["phys_page"]
            if p >= 0:
                front_sections.append((h0, p))
            prev_h0 = h0

    # Add Inleiding bookmarks (top-level, no children)
    for h0, p in front_sections:
        writer.add_outline_item(h0, p)

    # Add Briefwisseling + letter children
    for h0, p in body_sections:
        parent = writer.add_outline_item(h0, p)
        if h0 == "Briefwisseling":
            for n, t, lp in unique_letters:
                label = f"{n}  {t}" if t else str(n)
                writer.add_outline_item(label, lp, parent=parent)

    # ── 4d. BackMatter sections
    back = df[df["matter_type"] == "BackMatter"].copy()
    prev_h0 = None
    for _, row in back.iterrows():
        h0 = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
        if h0 and h0 not in ("nan", "no_value") and h0 != prev_h0:
            p = row["phys_page"]
            if p >= 0:
                writer.add_outline_item(h0, p)
            prev_h0 = h0

    # 5. Write output
    print(f"\nWriting '{OUTPUT_PDF}' …")
    with open(OUTPUT_PDF, "wb") as f:
        writer.write(f)

    size_mb = os.path.getsize(OUTPUT_PDF) / 1_000_000
    print(f"\n✓ Done! {OUTPUT_PDF}  ({size_mb:.1f} MB)")
    if failed:
        print(f"  ⚠  {len(failed)} pages were skipped due to download errors.")

if __name__ == "__main__":
    main()
