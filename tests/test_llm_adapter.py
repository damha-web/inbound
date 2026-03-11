import unittest

from agents.llm_adapter import MockLLMAdapter, OpenAIResponsesAdapter, make_llm_adapter


class LLMAdapterTests(unittest.TestCase):
    def test_factory_returns_mock(self) -> None:
        adapter = make_llm_adapter("mock")
        self.assertIsInstance(adapter, MockLLMAdapter)
        output = adapter.generate("hello")
        self.assertIn("[MOCK_GENERATED]", output)

    def test_factory_rejects_unknown_backend(self) -> None:
        with self.assertRaises(ValueError):
            make_llm_adapter("unknown")

    def test_openai_adapter_default_retries(self) -> None:
        adapter = OpenAIResponsesAdapter()
        self.assertEqual(adapter.max_retries, 2)


if __name__ == "__main__":
    unittest.main()
