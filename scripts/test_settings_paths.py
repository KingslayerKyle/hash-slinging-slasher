"""Search and reporting must read the same configured database."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import settings


class DatabasePaths(unittest.TestCase):
    def test_direct_csv_folder_and_custom_git_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            direct=root/'plain-tables'
            direct.mkdir()
            (direct/'names.csv').write_text('1,name\n',encoding='utf-8')
            checkout=root/'custom-database'
            (checkout/'csv').mkdir(parents=True)
            (checkout/'.git').write_text('gitdir: ../metadata\n',encoding='utf-8')
            (checkout/'csv/names.csv').write_text('2,name\n',encoding='utf-8')
            for configured,expected in [(direct,direct),(checkout,checkout/'csv')]:
                with patch.object(settings,'_values',return_value={'tables':str(configured)}):
                    self.assertEqual(Path(settings.tables_csv()),expected)

    def test_default_tables_resolve_to_adjacent_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'cod-name-db/csv').mkdir(parents=True)
            (root/'cod-name-db/csv/names.csv').write_text('3,name\n',encoding='utf-8')
            with patch.object(settings,'_values',return_value={'tables':str(root/'tables')}):
                self.assertEqual(Path(settings.tables_csv()),root/'cod-name-db/csv')
