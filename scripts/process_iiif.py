import os
import json
from pyvips import Image
import pandas as pd

# Configuration
p = os.getcwd()
workspace = os.getenv("GITHUB_WORKSPACE", ".")
GROUP = "retro"
SERIES = "heinsius"
BOOK = "heinsius_01_GS158"
BASE_URL = "http://jbw.do.local/{}/{}/{}/public/iiif".format(GROUP,SERIES,BOOK)
IMAGE_DIR = os.path.join(workspace, "{}/{}/{}/tiff".format(GROUP,SERIES,BOOK))
OUTPUT_DIR = os.path.join(workspace, "{}/{}/{}/public/iiif".format(GROUP,SERIES,BOOK))
CSV_PATH = os.path.join(workspace, "{}/{}/{}/dataset/csv/{}_by_page.csv".format(GROUP,SERIES,BOOK,BOOK))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_book():
    book_path = os.path.join(IMAGE_DIR)
    manifest_canvases = []
    
    # Sort files numerically/alphabetically (e.g., page_001.tif)
    # pages = sorted([f for f in os.listdir(book_path) if f.lower().endswith(('.tif', '.tiff'))])
    # pages = duckdb.sql("SELECT filebasename FROM '{}' ".format(CSV_PATH)).fetchnumpy()['filebasename']
    pages = pd.read_csv("{}".format(CSV_PATH))['filebasename'].tolist()
    for page in pages:
        page_id = page
        filename = page+".tif"
        tiff_file = os.path.join(book_path, filename)
        
        # 1. Open TIFF and convert to flat WebP (high quality, low storage footprint)
        img = Image.new_from_file(tiff_file)
        # webp_filename = f"{page_id}.webp"
        target_webp_path = os.path.join(OUTPUT_DIR, page_id, "full/full/0/default.webp")
        os.makedirs(os.path.dirname(target_webp_path), exist_ok=True)
        img.write_to_file(target_webp_path, Q=85) # 85% quality balances clarity and space
        
        # 2. Write compliant Tile-Free info.json (IIIF Image API v3 Level 0)
        info_json = {
            "@context": "http://iiif.io",
            "url": f"{BASE_URL}/{page_id}/full/full/0/default.webp",
            "type": "image",
            "protocol": "http://iiif.io",
            "profile": "level0", # Level 0 tells the viewer: No deep zoom tiles exist
            "width": img.width,
            "height": img.height
        }
        
        with open(os.path.join(OUTPUT_DIR,  page_id, "info.json"), "w") as f:
            json.dump(info_json, f, indent=2)
            
        # 3. Append metadata to the Presentation Canvas list
        # took out "service": [info_json] because it has no relevance at the moment
        manifest_canvases.append({
            "id": f"{BASE_URL}/canvas/{page_id}",
            "type": "Canvas",
            "label": {"en": [f"{page_id}"]},
            "width": img.width,
            "height": img.height,
            "items": [{
                "id": f"{BASE_URL}/{page_id}",
                "type": "AnnotationPage",
                "items": [{
                    "id": f"{BASE_URL}/annotation/{page_id}",
                    "type": "Annotation",
                    "motivation": "Book",
                    "body": {
                        "id": f"{BASE_URL}/{page_id}/full/full/0/default.webp",
                        "type": "Image",
                        "format": "image/webp",
                        "width": img.width,
                        "height": img.height
                    },
                    "target": f"{BASE_URL}/canvas/{page_id}"
                }]
            }]
        })

    # 4. Generate and write the book Manifest.json (IIIF Presentation v3)
    manifest = {
        "@context": "http://iiif.io",
        "id": f"{BASE_URL}/manifest.json",
        "type": "Manifest",
        "label": {"en": [f"Book - {BOOK}"]},
        "items": manifest_canvases
    }
    
    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

# Run for all subdirectories in the books folder
# for item in os.listdir(IMAGE_DIR):
#     print(item)
    # if os.path.isdir(os.path.join(IMAGE_DIR, item)):
        

        
process_book()
