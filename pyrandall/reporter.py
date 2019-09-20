import jsondiff

from pyrandall.types import Assertion, AssertionCall

SPACE = "  - "
ONE_SPACE = "    - "
TWO_SPACE = "      - "


class Reporter(object):
    def __init__(self):
        self.results = []
        self.failures = []

    def feature(self, text):
        """
            adds "scenario.feature" construct to the output buffer

            uses Scenario interface to get the title / description data
        """
        print(f"Feature: {text}")

    def scenario(self, text: str):
        """
            adds "scenario.feature.scenario" construct to the output buffer

            uses Scenario interface to get the title / description data
        """
        print(f"{SPACE}Scenario {text}")
        # TODO: move or clarify this method name
        rs = ResultSet(self)
        self.results.append(rs)
        return rs

    def simulate(self, text):
        """
            stores "scenario.feature.senario.simulate[]" items to the output buffer

            uses Scenario interface to get the title / description data
        """
        print(f"{ONE_SPACE}Simulate {text}")

    def validate(self, text):
        """
            stores "scenario.feature.senario.validate[]" items to the output buffer

            uses Scenario interface to get the title / description data
        """
        print(f"{ONE_SPACE}Validate {text}")

    def run_task(self, text):
        print(f"{ONE_SPACE}{text}")

    def print_assertion_failed(self, assertion_call, fail_text):
        # TODO: add assertion type (equal, greater than)
        print(
            f"{TWO_SPACE}assertion failed: {fail_text} did not equal, "
            f"expected: {assertion_call.expected} but got {assertion_call.actual}"
        )
        # This is redundant to the ResultSet tracking state
        self.failures.append(assertion_call)

    def print_assertion_passed(self, assertion_call: AssertionCall):
        print(f"{TWO_SPACE}{assertion_call}")

    def print_assertion_skipped(self, assertion_call: AssertionCall):
        print(f"{TWO_SPACE}{assertion_call}")
        pass

    def assertion(self, field, spec):
        return Assertion(field, spec, self)

    def print_failures(self):
        if self.failures:
            print("\nFailures:")
            for failed_assertion in self.failures:
                print(f"{ONE_SPACE}{failed_assertion}")

    def passed(self):
        return len(self.results) != 0 and all([rs.all() for rs in self.results])

    def failed_assertions(self):
        return self.failures

    def json_diff_report(expected, actual):
        return jsondiff.diff(expected, actual, syntax="explicit")


class ResultSet:
    def __init__(self, reporter):
        self.assertions = []
        self.reporter = reporter

    def all(self):
        return len(self.assertions) != 0 and all(self.assertions)

    def assertion_failed(self, assertion_call, fail_text):
        self.reporter.print_assertion_failed(assertion_call, fail_text)
        self.assertions.append(False)

    def assertion_passed(self, assertion_call: AssertionCall):
        self.reporter.print_assertion_passed(assertion_call)
        self.assertions.append(True)

    def assertion_skipped(self, assertion_call: AssertionCall):
        self.reporter.print_assertion_skipped(assertion_call)
        # True right?
        self.assertions.append(True)

    # Implement interface
    def run_task(self, text):
        self.reporter.run_task(text)
