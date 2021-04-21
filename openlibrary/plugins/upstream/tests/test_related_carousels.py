# -*- coding: utf-8 -*-
from .. import models


def test_related_subjects():
    subjects = set(
        [
            "In library",
            "Conduct of life",
            "London (England)",
            "Science Fiction & Fantasy",
            "Self-experimentation in medicine in fiction",
            "Accessible book",
            "Physicians in fiction",
            "Fiction",
            "England in fiction",
            "OverDrive",
            "Supernatural",
            "Scottish Horror tales",
            "Horror fiction",
            "Mystery and detective stories",
            "Physicians",
            "Horror",
            "Classic Literature",
            "Open Library Staff Picks",
            "Protected DAISY",
            "Self-experimentation in medicine",
            "open_syllabus_project",
            "Multiple personality in fiction",
            "Conduct of life in fiction",
            "Supernatural in fiction",
            "Juvenile fiction",
            "History and criticism",
            "Horror tales",
            "English fiction",
            "Social conditions",
            "Horror stories",
            "Multiple personality",
            "Internet Archive Wishlist",
            "François",
            "Remove period.",
            "Remove &",
            "remove '",
        ]
    )
    expected_subjects = set(
        [
            "Conduct of life",
            "Physicians in fiction",
            "England in fiction",
            "Supernatural",
            "Scottish Horror tales",
            "Horror fiction",
            "Mystery and detective stories",
            "Physicians",
            "Horror",
            "Classic Literature",
            "Multiple personality in fiction",
            "Conduct of life in fiction",
            "Supernatural in fiction",
            "Juvenile fiction",
            "History and criticism",
            "Horror tales",
            "English fiction",
            "Social conditions",
            "Horror stories",
            "Multiple personality",
        ]
    )
    actual_subjects = set(models.Work.filter_problematic_subjects(subjects))
    assert (actual_subjects ^ expected_subjects) == set([])
