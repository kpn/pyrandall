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
            resultset = reporter.scenario(scenario.description)

            if self.flags & Flags.SIMULATE:
                reporter.simulate(scenario.simulate_adapter)
                for spec in scenario.simulate_tasks:
                    # creating a executor for the spec in simulate_tasks
                    # with it, a new task reporter that will report success or not
                    if scenario.simulate_adapter == Adapter.REQUESTS_HTTP:
                        e = executors.RequestHttpEvents(spec)
                    elif scenario.simulate_adapter == Adapter.BROKER_KAFKA:
                        e = executors.BrokerKafka(spec)
                    else:
                        raise NotImplementedError("no such adapter implemented")
                    reporter.run_task(e.represent())
                    e.execute(resultset)

            if self.flags & Flags.VALIDATE:
                reporter.validate(scenario.validate_adapter)
                for spec in scenario.validate_tasks:
                    if scenario.validate_adapter == Adapter.REQUESTS_HTTP:
                        e = executors.RequestHttp(spec)
                    elif scenario.validate_adapter == Adapter.BROKER_KAFKA:
                        e = executors.BrokerKafka(spec)
                    else:
                        raise NotImplementedError("no such adapter implemented")
                    reporter.run_task(e.represent())
                    e.execute(resultset)
