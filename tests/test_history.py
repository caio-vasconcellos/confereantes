import unittest
from pathlib import Path

from confereantes.history import HistoryStore
from confereantes.risk_engine import analyze


class HistoryStoreTests(unittest.TestCase):
    def test_saves_reads_and_clears_encrypted_history(self) -> None:
        store = HistoryStore(Path.cwd() / ".test-history")
        store.clear()
        result = analyze(received_text="Faça o Pix agora.")
        entry_id = store.save(
            result,
            original_text="Produto por R$ 100,00",
            received_text="Faça o Pix agora.",
        )

        entries = store.list()
        self.assertGreater(entry_id, 0)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].score, result.score)
        self.assertIn("Produto", entries[0].original_excerpt)

        raw_database = store.database_path.read_bytes()
        self.assertNotIn("Produto por R$ 100,00".encode(), raw_database)

        store.clear()
        self.assertEqual(store.list(), [])


if __name__ == "__main__":
    unittest.main()
