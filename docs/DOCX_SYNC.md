# Microsoft Word DOCX Synchronizer (`docx_sync`)
> **Domain F: Retrieval & Infrastructure** | **CLI:** `arcanum docx-sync`

---

## 1. Overview & Theoretical Rationale
The **DOCX Synchronizer** allows authors to collaborate with literary editors, agents, and beta readers who work in Microsoft Word without compromising the markdown source of truth or leaking files to cloud conversion servers.

---

## 2. Headless XML Extraction Logic
The engine directly parses the zipped OpenXML structure of `.docx` files using standard library `zipfile` and `xml.etree.ElementTree`:
- Reads `<w:body>` paragraph runs (`<w:p>`, `<w:r>`).
- Translates Word comments (`word/comments.xml`) into inline markdown callout annotations (`> [!NOTE] Comment: ...`).
- Maps Word heading styles (`Heading 1`, `Heading 2`) to Markdown `#` and `##` hierarchies.

---

## 3. CLI Command Examples
```bash
# Export chapter to styled Word document for beta readers
arcanum docx-sync export 01_Manuscript/Chapter_01.md --output review.docx

# Ingest edited Word document and extract editorial comments
arcanum docx-sync import review_edited.docx --target 01_Manuscript/Chapter_01.md
```
