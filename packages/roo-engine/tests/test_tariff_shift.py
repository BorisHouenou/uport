"""Unit tests for Tariff Shift calculations."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from models import BOMLine
from tariff_shift import check_change_in_chapter, check_change_in_heading, check_change_in_subheading


def make_line(hs: str, originating: bool | None = False) -> BOMLine:
    return BOMLine(description="Test part", hs_code=hs, origin_country="CN", unit_cost=10.0, is_originating=originating)


class TestChangeInChapter:
    def test_passes_when_different_chapter(self):
        bom = [make_line("8544.42")]   # chapter 85, output is chapter 87
        result = check_change_in_chapter(bom, output_hs="8703.22")
        assert result.passes is True
        assert result.shift_level == "chapter"

    def test_fails_when_same_chapter(self):
        bom = [make_line("8703.10")]   # both chapter 87
        result = check_change_in_chapter(bom, output_hs="8703.22")
        assert result.passes is False

    def test_originating_inputs_ignored(self):
        bom = [make_line("8703.10", originating=True)]  # same chapter but originating → exempt
        result = check_change_in_chapter(bom, output_hs="8703.22")
        assert result.passes is True  # no non-originating violations

    def test_mixed_bom(self):
        bom = [
            make_line("7326.90", originating=False),   # chapter 73 ≠ 87 → OK
            make_line("8544.42", originating=False),   # chapter 85 ≠ 87 → OK
        ]
        result = check_change_in_chapter(bom, output_hs="8703.22")
        assert result.passes is True

    def test_fails_with_one_same_chapter_input(self):
        bom = [
            make_line("7326.90", originating=False),   # OK
            make_line("8703.10", originating=False),   # FAIL — same chapter 87
        ]
        result = check_change_in_chapter(bom, output_hs="8703.22")
        assert result.passes is False

    def test_no_non_originating_inputs_passes(self):
        bom = [make_line("8703.10", originating=True)]
        result = check_change_in_chapter(bom, output_hs="8703.22")
        assert result.passes is True


class TestChangeInHeading:
    def test_passes_different_heading(self):
        bom = [make_line("8708.40")]   # heading 8708 ≠ 8703
        result = check_change_in_heading(bom, output_hs="8703.22")
        assert result.passes is True

    def test_fails_same_heading(self):
        bom = [make_line("8703.10")]   # heading 8703 == 8703
        result = check_change_in_heading(bom, output_hs="8703.22")
        assert result.passes is False


class TestChangeInSubheading:
    def test_passes_different_subheading(self):
        bom = [make_line("8703.10")]   # sub 870310 ≠ 870322
        result = check_change_in_subheading(bom, output_hs="8703.22")
        assert result.passes is True

    def test_fails_same_subheading(self):
        bom = [make_line("8703.22")]
        result = check_change_in_subheading(bom, output_hs="8703.22")
        assert result.passes is False
