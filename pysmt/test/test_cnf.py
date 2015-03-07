#
# This file is part of pySMT.
#
#   Copyright 2014 Andrea Micheli and Marco Gario
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import unittest
import os
from nose.plugins.attrib import attr

from pysmt.shortcuts import Implies, is_sat, is_valid, reset_env
from pysmt.cnf import CNFizer
from pysmt.logics import QF_BOOL, QF_LRA, QF_LIA, UFLIRA
from pysmt.test import TestCase, skipIfNoSolverForLogic
from pysmt.test.examples import EXAMPLE_FORMULAS
from pysmt.test.smtlib.parser_utils import SMTLIB_TEST_FILES, SMTLIB_DIR
from pysmt.smtlib.parser import get_formula_fname

class TestCnf(TestCase):

    def do_examples(self, logic):
        conv = CNFizer()
        for example in EXAMPLE_FORMULAS:
            if example.logic != logic:
                continue
            cnf = conv.convert_as_formula(example.expr)

            res = is_valid(Implies(cnf, example.expr), logic=logic)
            self.assertTrue(res)

            res = is_sat(cnf, logic=logic)
            self.assertEqual(res, example.is_sat)


    @skipIfNoSolverForLogic(QF_BOOL)
    def test_examples_solving_bool(self):
        self.do_examples(QF_BOOL)

    @skipIfNoSolverForLogic(QF_LRA)
    def test_examples_solving_lra(self):
        self.do_examples(QF_LRA)

    @skipIfNoSolverForLogic(QF_LIA)
    def test_examples_solving_lia(self):
        self.do_examples(QF_LIA)

    @skipIfNoSolverForLogic(QF_LIA)
    def test_smtlib_cnf_small(self):
        cnt = 0
        max_cnt = 3
        for (logic, f, expected_result) in SMTLIB_TEST_FILES:
            if logic != QF_LIA:
                continue
            self._smtlib_cnf(f, logic, expected_result=="sat")
            cnt += 1
            if cnt == max_cnt:
                break

    @attr("slow")
    @skipIfNoSolverForLogic(UFLIRA)
    def test_smtlib_cnf(self):
        for (logic, f, expected_result) in SMTLIB_TEST_FILES:
            self._smtlib_cnf(f, logic, expected_result=="sat")

    def _smtlib_cnf(self, filename, logic, res_is_sat):
        reset_env()
        conv = CNFizer()
        smtfile = os.path.join(SMTLIB_DIR, filename)
        assert os.path.exists(smtfile)

        expr = get_formula_fname(smtfile)
        expr = expr[0] ## MG: WHY -- This seems to be a bug of get_formula_fname.
        if not logic.quantifier_free:
            with self.assertRaises(NotImplementedError):
                conv.convert_as_formula(expr)
            return
        print(len(str(expr)))
        cnf = conv.convert_as_formula(expr)
        res = is_valid(Implies(cnf, expr), logic=logic)
        self.assertTrue(res)

        res = is_sat(cnf, logic=logic)
        self.assertEqual(res, res_is_sat)

if __name__ == '__main__':
    unittest.main()
