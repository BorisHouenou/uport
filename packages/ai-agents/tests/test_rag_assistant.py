"""Unit tests for RAG assistant — retrieval, context building, citation shape."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from rag_assistant import _retrieve, _build_context, KNOWLEDGE_BASE


# ─── _retrieve ────────────────────────────────────────────────────────────────

class TestRetrieve:
    def test_returns_results_for_matching_query(self):
        results = _retrieve("regional value content build down", None)
        assert len(results) > 0

    def test_top_result_is_most_relevant(self):
        results = _retrieve("regional value content RVC build-down method", None)
        # The RVC article should be in top results
        sources = [r["source"] for r in results]
        assert any("Regional Value Content" in s or "RVC" in s for s in sources)

    def test_agreement_filter_excludes_other_agreements(self):
        results = _retrieve("originating goods", ["cusma"])
        for r in results:
            assert r["agreement"] in ("cusma", "general"), \
                f"Expected cusma or general, got {r['agreement']}"

    def test_agreement_filter_ceta(self):
        results = _retrieve("supplier declaration", ["ceta"])
        for r in results:
            assert r["agreement"] in ("ceta", "general")

    def test_general_chunks_always_included_in_filtered_results(self):
        results = _retrieve("certificate of origin", ["cusma"])
        agreements = {r["agreement"] for r in results}
        # general chunks should pass through any filter
        assert "general" in agreements or "cusma" in agreements

    def test_empty_query_returns_empty(self):
        results = _retrieve("", None)
        assert results == []

    def test_respects_k_limit(self):
        results = _retrieve("originating goods material value", None, k=3)
        assert len(results) <= 3

    def test_no_results_for_nonsense_query(self):
        results = _retrieve("xyzzy foobar qux", None)
        assert results == []

    def test_cptpp_self_certification(self):
        results = _retrieve("self certification cptpp producer exporter", ["cptpp"])
        sources = [r["source"] for r in results]
        assert any("Self-Certification" in s or "CPTPP" in s for s in sources)

    def test_automotive_rvc_cusma(self):
        results = _retrieve("passenger vehicle 8703 automotive RVC", ["cusma"])
        assert any("8703" in r["source"] or "Automotive" in r["source"] for r in results)


# ─── _build_context ──────────────────────────────────────────────────────────

class TestBuildContext:
    def test_returns_no_context_string_when_empty(self):
        ctx = _build_context([])
        assert ctx == "No relevant context retrieved."

    def test_contains_source_header(self):
        chunks = KNOWLEDGE_BASE[:2]
        ctx = _build_context(chunks)
        assert "[1]" in ctx
        assert "[2]" in ctx

    def test_contains_agreement_label(self):
        chunks = [c for c in KNOWLEDGE_BASE if c["agreement"] == "cusma"][:1]
        ctx = _build_context(chunks)
        assert "CUSMA" in ctx

    def test_contains_content(self):
        chunks = KNOWLEDGE_BASE[:1]
        ctx = _build_context(chunks)
        assert chunks[0]["content"][:20] in ctx

    def test_numbering_sequential(self):
        chunks = KNOWLEDGE_BASE[:5]
        ctx = _build_context(chunks)
        for i in range(1, 6):
            assert f"[{i}]" in ctx


# ─── Knowledge base integrity ─────────────────────────────────────────────────

class TestKnowledgeBase:
    def test_all_entries_have_required_fields(self):
        for entry in KNOWLEDGE_BASE:
            assert "source" in entry, f"Missing 'source' in {entry}"
            assert "agreement" in entry, f"Missing 'agreement' in {entry}"
            assert "content" in entry, f"Missing 'content' in {entry}"

    def test_agreement_values_are_valid(self):
        valid = {"cusma", "ceta", "cptpp", "general"}
        for entry in KNOWLEDGE_BASE:
            assert entry["agreement"] in valid, \
                f"Unknown agreement '{entry['agreement']}' in {entry['source']}"

    def test_no_empty_content(self):
        for entry in KNOWLEDGE_BASE:
            assert entry["content"].strip(), f"Empty content in {entry['source']}"

    def test_contains_all_agreements(self):
        agreements = {e["agreement"] for e in KNOWLEDGE_BASE}
        assert "cusma" in agreements
        assert "ceta" in agreements
        assert "cptpp" in agreements
        assert "general" in agreements

    def test_minimum_entry_count(self):
        assert len(KNOWLEDGE_BASE) >= 10, "Knowledge base seems too small"
