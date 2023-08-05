# -*- coding: utf-8 -*-
"""
PyUnit unit tests
"""
import unittest
import sys
try:
    import json
except ImportError:
    import simplejson as json
import json_diff
from StringIO import StringIO
import codecs

from test_strings import ARRAY_DIFF, ARRAY_NEW, ARRAY_OLD, \
    NESTED_DIFF, NESTED_DIFF_EXCL, NESTED_DIFF_INCL, NESTED_NEW, NESTED_OLD, \
    NO_JSON_NEW, NO_JSON_OLD, SIMPLE_ARRAY_DIFF, SIMPLE_ARRAY_NEW, \
    NESTED_DIFF_IGNORING, \
    SIMPLE_ARRAY_OLD, SIMPLE_DIFF, SIMPLE_DIFF_HTML, SIMPLE_NEW, SIMPLE_OLD


class OptionsClass(object):
    def __init__(self, inc=None, exc=None, ign=None):
        self.exclude = exc
        self.include = inc
        self.ignore_append = ign


class OurTestCase(unittest.TestCase):
    def _run_test(self, oldf, newf, difff, msg="", opts=None):
        diffator = json_diff.Comparator(oldf, newf, opts)
        diff = diffator.compare_dicts()
        expected = json.load(difff)
        self.assertEqual(json.dumps(diff, sort_keys=True),
                         json.dumps(expected, sort_keys=True),
                         msg + "\n\nexpected = %s\n\nobserved = %s" %
                         (json.dumps(expected, sort_keys=True, indent=4,
                                     ensure_ascii=False),
                          json.dumps(diff, sort_keys=True, indent=4,
                                     ensure_ascii=False)))

    def _run_test_strings(self, olds, news, diffs, msg="", opts=None):
        self._run_test(StringIO(olds), StringIO(news), StringIO(diffs),
            msg, opts)

    def _run_test_formatted(self, oldf, newf, difff, msg="", opts=None):
        diffator = json_diff.Comparator(oldf, newf, opts)
        diff = ("\n".join([line.strip() \
                for line in unicode(\
                    json_diff.HTMLFormatter(diffator.compare_dicts())).\
                           split("\n")])).strip()
        expected = ("\n".join([line.strip() for line in difff if line])).\
            strip()
        self.assertEqual(diff, expected, msg +
                         "\n\nexpected = %s\n\nobserved = %s" %
                         (expected, diff))


class TestBasicJSON(OurTestCase):
    def test_empty(self):
        diffator = json_diff.Comparator({}, {})
        diff = diffator.compare_dicts()
        self.assertEqual(json.dumps(diff).strip(), "{}",
             "Empty objects diff.\n\nexpected = %s\n\nobserved = %s" %
             ({}, diff))

    def test_null(self):
        self._run_test_strings('{"a": null}', '{"a": null}',
            '{}', "Nulls")

    def test_null_to_string(self):
        self._run_test_strings('{"a": null}', '{"a": "something"}',
            '{"_update": {"a": "something"}}', "Null changed to string")

    def test_boolean(self):
        self._run_test_strings('{"a": true}', '{"a": false}',
            '{"_update": {"a": false}}', "Booleans")

    def test_integer(self):
        self._run_test_strings(u'{"a": 1}', '{"a": 2}',
            u'{"_update": {"a": 2}}', "Integers")

    def test_float(self):
        self._run_test_strings(u'{"a": 1.0}', '{"a": 1.1}',
            u'{"_update": {"a": 1.1}}', "Floats")

    def test_int_to_float(self):
        self._run_test_strings(u'{"a": 1}', '{"a": 1.0}',
            u'{"_update": {"a": 1.0}}', "Integer changed to float")

    def test_simple(self):
        self._run_test_strings(SIMPLE_OLD, SIMPLE_NEW, SIMPLE_DIFF,
                "All-scalar objects diff.")

    def test_simple_formatted(self):
        self._run_test_formatted(StringIO(SIMPLE_OLD), StringIO(SIMPLE_NEW),
            StringIO(SIMPLE_DIFF_HTML),
            "All-scalar objects diff (formatted).")

    def test_simple_array(self):
        self._run_test_strings(SIMPLE_ARRAY_OLD, SIMPLE_ARRAY_NEW,
            SIMPLE_ARRAY_DIFF, "Simple array objects diff.")

    def test_another_array(self):
        self._run_test_strings(ARRAY_OLD, ARRAY_NEW,
            ARRAY_DIFF, "Array objects diff.")


class TestHappyPath(OurTestCase):
    def test_realFile(self):
        self._run_test(open("test/old.json"), open("test/new.json"),
            open("test/diff.json"), "Simply nested objects (from file) diff.")

    def test_nested(self):
        self._run_test_strings(NESTED_OLD, NESTED_NEW, NESTED_DIFF,
            "Nested objects diff.")

    def test_nested_formatted(self):
        self._run_test_formatted(open("test/old.json"), open("test/new.json"),
            codecs.open("test/nested_html_output.html", "r", "utf-8"),
            "Simply nested objects (from file) diff formatted as HTML.")

    def test_nested_excluded(self):
        self._run_test_strings(NESTED_OLD, NESTED_NEW, NESTED_DIFF_EXCL,
            "Nested objects diff with exclusion.",
            OptionsClass(exc=["nome"]))

    def test_nested_included(self):
        self._run_test_strings(NESTED_OLD, NESTED_NEW, NESTED_DIFF_INCL,
            "Nested objects diff.", OptionsClass(inc=["nome"]))

    def test_nested_ignoring_append(self):
        self._run_test_strings(NESTED_OLD, NESTED_NEW, NESTED_DIFF_IGNORING,
            "Nested objects diff.", OptionsClass(ign=True))


class TestadPath(OurTestCase):
    def test_no_JSON(self):
        self.assertRaises(json_diff.BadJSONError,
                json_diff.Comparator, StringIO(NO_JSON_OLD),
                StringIO(NO_JSON_NEW)
        )

    def test_bad_JSON_no_hex(self):
        self.assertRaises(json_diff.BadJSONError, self._run_test_strings,
            u'{"a": 0x1}', '{"a": 2}', u'{"_update": {"a": 2}}',
            "Hex numbers not supported")

    def test_bad_JSON_no_octal(self):
        self.assertRaises(json_diff.BadJSONError, self._run_test_strings,
            u'{"a": 01}', '{"a": 2}', u'{"_update": {"a": 2}}',
            "Octal numbers not supported")


class TestPiglitData(OurTestCase):
    def test_piglit_result_only(self):
        self._run_test(open("test/old-testing-data.json"),
            open("test/new-testing-data.json"),
            open("test/diff-result-only-testing-data.json"),
            "Large piglit reports diff (just resume field).",
            OptionsClass(inc=["result"]))

#    def test_piglit_results(self):
#        self._run_test(open("test/old-testing-data.json"),
#            open("test/new-testing-data.json"),
#            open("test/diff-testing-data.json"), "Large piglit results diff.")


class TestMainArgsMgmt(unittest.TestCase):
    def test_args_help(self):
        save_stdout = StringIO()
        sys.stdout = save_stdout

        try:
            json_diff.main(["./test_json_diff.py", "-h"])
        except SystemExit:
            save_stdout.seek(0)
            sys.stdout = sys.__stdout__
            expected = "Usage:"
            observed = save_stdout.read()

        self.assertEquals(observed[:len(expected)], expected,
            "testing -h usage message")

    def test_args_run_same(self):
        save_stdout = StringIO()
        sys.stdout = save_stdout

        res = json_diff.main(["./test_json_diff.py",
            "test/old.json", "test/old.json"])

        sys.stdout = sys.__stdout__
        self.assertEquals(res, 0, "testing -h usage message")

    def test_args_run_different(self):
        save_stdout = StringIO()
        sys.stdout = save_stdout

        res = json_diff.main(["./test_json_diff.py",
            "test/old.json", "test/new.json"])

        sys.stdout = sys.__stdout__
        self.assertEquals(res, 1, "testing -h usage message")

if __name__ == "__main__":
    unittest.main()
