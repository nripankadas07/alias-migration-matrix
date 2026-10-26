import unittest
from alias_migration_matrix import analyze


def model(aliases, **kwargs):
    return {'fields': [{'name': 'asset', 'type': 'str', 'aliases': aliases}], **kwargs}


class Matrix(unittest.TestCase):
    def test_dropped_key_and_precedence(self):
        r = analyze({'old': model(['id', 'asset_id']), 'new': model(['asset_id', 'id'])})
        changed = [c for c in r['cases'] if c['change'] == 'VALUE_CHANGED']
        self.assertEqual(len(changed), 1)
        self.assertNotEqual(changed[0]['old']['values'], changed[0]['new']['values'])
        r = analyze({'old': model(['id', 'asset_id']), 'new': model(['asset_id'])})
        self.assertTrue(any(c['payload'] == {'id': 'asset:sample'} and c['change'] == 'REJECTED_AFTER' for c in r['cases']))

    def test_name_and_extra_policy(self):
        r = analyze({'old': model(['id'], validate_by_name=True), 'new': model(['id'], extra='forbid')})
        self.assertTrue(any(c['change'] == 'REJECTED_AFTER' for c in r['cases']))

    def test_shared_alias_fans_into_fields(self):
        a = {'fields': [{'name': 'a', 'type': 'str', 'aliases': ['x', 'y']}, {'name': 'b', 'type': 'str', 'aliases': ['x', 'z']}]}
        r = analyze({'old': a, 'new': a})
        self.assertTrue(any(c['old']['accepted'] and c['old']['values']['a'] == c['old']['values']['b'] for c in r['cases']))
        self.assertEqual(r['counts']['UNCHANGED'], r['tested_payloads'])

    def test_no_user_code_and_limit(self):
        for bad in [{'fields': [{'name': 'model_dump', 'type': 'str'}]}, {'fields': [{'name': 'x', 'type': '__import__'}]}, {'fields': [{'name': str(i), 'type': 'int'} for i in range(7)]}]:
            with self.assertRaises(ValueError):
                analyze({'old': bad, 'new': model(['x'])})


if __name__ == '__main__':
    unittest.main()
