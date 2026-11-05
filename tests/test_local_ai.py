import json
import unittest
from unittest.mock import patch

import httpx

from confereantes.local_ai import explain, LocalAIUnavailable
from confereantes.main import _process
from confereantes.risk_engine import analyze


class LocalAITests(unittest.TestCase):
    def test_only_sends_rule_labels_not_personal_evidence(self):
        requests = []

        def respond(request):
            requests.append(request)
            if request.url.path == "/api/show":
                return httpx.Response(200, json={"details": {"family": "qwen2"}})
            return httpx.Response(200, json={"response": "Confirme a solicitação por outro canal."})

        client = httpx.Client(base_url="http://127.0.0.1:11434", transport=httpx.MockTransport(respond))
        result = analyze(received_text="Faça Pix agora para Pessoa Particular 123456.")
        with patch("confereantes.local_ai.httpx.Client", return_value=client):
            text, model = explain(result)
        self.assertTrue(text)
        self.assertEqual(model, "qwen2.5:0.5b")
        data = json.loads(requests[-1].content)
        self.assertNotIn("Pessoa Particular", json.dumps(data))
        self.assertNotIn("123456", json.dumps(data))
        self.assertEqual(data["options"]["temperature"], 0)

    def test_rejects_remote_model_before_generating(self):
        def respond(request):
            self.assertEqual(request.url.path, "/api/show")
            return httpx.Response(200, json={"remote_host": "https://remote.invalid"})
        client = httpx.Client(base_url="http://127.0.0.1:11434", transport=httpx.MockTransport(respond))
        with patch("confereantes.local_ai.httpx.Client", return_value=client), self.assertRaises(LocalAIUnavailable):
            explain(analyze(received_text="Pix agora"))

    def test_unavailable_ai_preserves_rule_score(self):
        data = {"received_text": "Envie sua senha e token agora."}
        expected = analyze(**data)
        with patch("confereantes.main.explain", side_effect=LocalAIUnavailable("Sem modelo")):
            actual = _process(data, True)
        self.assertEqual(actual.score, expected.score)
        self.assertEqual(actual.findings, expected.findings)
        self.assertEqual(actual.explanation_error, "Sem modelo")
