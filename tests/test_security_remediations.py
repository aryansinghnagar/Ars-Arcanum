import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.docx_sync import convert_docx_to_markdown
from lib.importer import extract_docx_text
from lib.codex_export import build_single_file_codex, scan_world_vault


class TestSecurityRemediations(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sec02_codex_export_csp_and_xss_defense(self):
        """Validates that codex export generates strict CSP and escapes HTML injections."""
        notes_dir = self.root / "World"
        notes_dir.mkdir()
        (notes_dir / "bad.md").write_text(
            '---\ntitle: "Bad </script><script>alert(1)</script>"\ncategory: "Characters"\n---\n<script>alert(2)</script>',
            encoding="utf-8"
        )
        html_out = self.root / "codex.html"
        cats = scan_world_vault(notes_dir)
        build_single_file_codex(
            categories=cats,
            world_name="TestWorld",
            output_path=html_out,
        )
        self.assertTrue(html_out.is_file())
        content = html_out.read_text(encoding="utf-8")
        # Content Security Policy must be present
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)

    def test_sec03_docx_and_importer_xxe_buffer_full_scan(self):
        """Validates that XML buffers larger than 4KB with <!ENTITY at the end are flagged."""
        padding = "<!-- " + ("A" * 5000) + " -->\n"
        xxe_xml = padding + '<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>&xxe;</w:t></w:r></w:p></w:body></w:document>'

        # Create docx zip with malicious document.xml
        evil_docx = self.root / "malicious.docx"
        with zipfile.ZipFile(evil_docx, "w") as zf:
            zf.writestr("word/document.xml", xxe_xml.encode("utf-8"))

        with self.assertRaises(ValueError) as cm_docx:
            convert_docx_to_markdown(evil_docx)
        self.assertIn("Unsafe XML entity", str(cm_docx.exception))

        with self.assertRaises(ValueError) as cm_importer:
            extract_docx_text(evil_docx)
        self.assertIn("Unsafe DOCTYPE/ENTITY", str(cm_importer.exception))


if __name__ == "__main__":
    unittest.main()

