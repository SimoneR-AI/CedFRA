import docx
from docx.oxml.ns import qn

APP_DIR = "d:/Users/Robbiani Simone/AntiG/CedFRA_antigrav"
TEMPLATE_PATH = f"{APP_DIR}/app/templates/template_pagamento.docx"

doc = docx.Document(TEMPLATE_PATH)
t = doc.tables[0]

# Row 0 has a fixed height of 841 due to the previous layout. We remove it.
row = t.rows[0]
trPr = row._tr.find(qn("w:trPr"))
if trPr is not None:
    trHeight = trPr.find(qn("w:trHeight"))
    if trHeight is not None:
        trPr.remove(trHeight)
        print("Removed fixed height from Row 0.")

# Maybe just to make sure, let's also ensure Row 1 has its height. (It already has 404).

doc.save(TEMPLATE_PATH)
