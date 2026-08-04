"""
tesseract v4.1.1.20191227
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_text(image):
    tessdata_dir_config = r'--tessdata-dir Q:\Digitaal_Databeheer\migratie_resources\resources\tessdata_best-main --psm 1 --oem 1'
    text = pytesseract.image_to_string(image, config=tessdata_dir_config, lang="nld+fra", timeout=60
    return text

before save:
text = ocr_text(image).replace('”','"').replace('“','"').replace('„','"').replace('”','"').replace('’','\'')

"""

# In the site generator for compatibility use a number of names for 
# pieces of information we need to create the site.
# In this list connect a SSG name with the actual name of the column in the CSV
def all_references():
    references={   
                "matter_type" : "matter_type",
                "page_number" : "page_number",
                "file_number" : "file_number",
                "item_number" : "item_number",
                "scan" : "image_url",
                "prev_filename" : "previous_filebasename",
                "next_filename" : "next_filebasename",
                "filename" : "filebasename",
                "link_text" : "title",
                "first_line" : "fline",
                "sort" : "id",
                "ocr" : "ocr_v2",
                "bibrec" : "bibrec"
                }
    tocs = [
            {"stitle":"Index by items",
            "ltitle":"Index by items",
            "columns":{"Letter_number":"item_number","from":"item_from","to":"item_to","dated":"date_as_object"},
            "page_number":"page_number"}
            ]
    
    return references, tocs
