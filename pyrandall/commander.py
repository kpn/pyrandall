from . import executors
from .reporter import Reporter
from .spec import Adapter
from .types import Flags


class Commander:
    def __init__(self, spec, flags: Flags):
        self.spec = spec
        self.flags = flags

    def invoke(self):
        success = self.run(Reporter())
        if success:
            raise SystemExit(0)
        else:
            raise SystemExit(1)

    def run(self, reporter):
        # options allow to:
        # - only simulate
        # - only validate
        # - consecutively simulate and validate
        reporter.feature(self.spec.description)
        self.run_scenarios(self.spec.scenario_items, reporter)
        reporter.print_failures()
        return reporter.passed()

    def run_scenarios(self, scenario_items, reporter):
        for scenario in scenario_items:
            # Commander responsible to implement how these functions are executed
            # for example in parallel, blocking, non blocking etc.
            # as a consequence: total execution time needs to be measured here,
            # Reporter is responsible for overall passing or failing of a test
            # 2 things:
            # 1. success/failure per test and overall
            # 2. call output interface
            reporter.scenario(scenario.description)

            if self.flags & Flags.SIMULATE:
                reporter.simulate()
                resultset = reporter.create_and_track_resultset()
                for spec in scenario.simulate_tasks:
                    e = self.executor_factory(spec)
                    reporter.run_task(e.represent())
                    e.execute(resultset)

            if self.flags & Flags.VALIDATE:
                reporter.validate()
                resultset = reporter.create_and_track_resultset()
                for spec in scenario.validate_tasks:
                    e = self.executor_factory(spec)
                    reporter.run_task(e.represent())
                    e.execute(resultset)

    def executor_factory(self, spec):
        # each spec can be run with an executor
        # based on the adapter defined on the spec
        if spec.adapter == Adapter.REQUESTS_HTTP:
            return executors.RequestHttp(spec)
        elif spec.adapter == Adapter.REQUEST_HTTP_EVENTS:
            return executors.RequestHttpEvents(spec)
        elif spec.adapter == Adapter.BROKER_KAFKA:
            return executors.BrokerKafka(spec)
        else:
            raise NotImplementedError("no such adapter implemented")
