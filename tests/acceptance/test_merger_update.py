# -*- coding: utf-8 -*-
#
# This file is part of Inspirehep.
# Copyright (C) 2016 CERN.
#
# Inspirehep is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Inspirehep is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inspirehep; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Acceptance scenarios for the merger."""

from __future__ import absolute_import, print_function

import pytest

from json_merger import UpdateMerger, MergeError
from json_merger.contrib.inspirehep.comparators import AuthorComparator
from json_merger.comparator import PrimaryKeyComparator
from json_merger.conflict import Conflict, ConflictType
from json_merger.list_unify import UnifierOps


class TitleComparator(PrimaryKeyComparator):

    primary_key_fields = ['source']


class AffiliationComparator(PrimaryKeyComparator):

    primary_key_fields = ['value']


COMPARATORS = {
    'authors': AuthorComparator,
    'authors.affiliations': AffiliationComparator,
    'titles': TitleComparator
}
LIST_MERGE_OPS = {
    'titles': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'authors.affiliations': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST
}


def _deserialize_conflict(conflict_type, path, body):
    if conflict_type == ConflictType.MANUAL_MERGE:
        body = tuple(body)
    return Conflict(conflict_type, tuple(path), body)


@pytest.mark.parametrize('scenario', [
    'author_typo_update_fix',
    'author_typo_curator_fix',
    'author_typo_update_and_curator_fix',
    'author_typo_conflict',
    'author_prepend_and_curator_typo_fix',
    'author_delete_and_single_curator_typo_fix',
    'author_delete_and_double_curator_typo_fix',
    'author_reorder_and_double_curator_typo_fix',
    'author_reorder_conflict',
    'author_replace_and_single_curator_typo_fix',
    'author_delete_and_double_curator_typo_fix',
    'author_curator_collab_addition',
    'author_affiliation_addition',
    'title_addition',
    'title_change'])
def test_author_typo_scenarios(update_fixture_loader, scenario):
    root, head, update, exp, desc = update_fixture_loader.load_test(scenario)
    merger = UpdateMerger(root, head, update,
                          comparators=COMPARATORS,
                          list_merge_ops=LIST_MERGE_OPS)
    if exp.get('conflicts'):
        with pytest.raises(MergeError) as excinfo:
            merger.merge()
        expected_conflicts = [_deserialize_conflict(t, p, b)
                              for t, p, b in exp.pop('conflicts')]
        assert set(expected_conflicts) == set(excinfo.value.content)
    else:
        merger.merge()

    assert merger.merged_root == exp, desc


@pytest.mark.xfail
@pytest.mark.parametrize('scenario', ['author_double_match_conflict'])
def test_autor_xfail_scenarios(update_fixture_loader, scenario):
    test_author_typo_scenarios(update_fixture_loader, scenario)
