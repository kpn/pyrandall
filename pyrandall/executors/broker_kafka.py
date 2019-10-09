from pyrandall.kafka import KafkaConn
from pyrandall.types import Assertion, ExecutionMode, UnorderedDiffAssertion
from .common import Executor


class BrokerKafka(Executor):
    def __init__(self, spec, *args, **kwargs):
        super().__init__()
        self.execution_mode = spec.execution_mode
        self.spec = spec

    def execute(self, reporter):
        if self.execution_mode is ExecutionMode.SIMULATING:
            self.simulate(self.spec, reporter)
        elif self.execution_mode is ExecutionMode.VALIDATING:
            self.validate(self.spec, reporter)

    def simulate(self, spec, reporter):
        kafka = KafkaConn()
        kafka.init_producer()

        with Assertion(
            "events_produced", spec.assertions, "produced a event", reporter
        ) as a:
            send = 0
            for event in spec.events:
                kafka.produce_message(spec.topic, event)
                send += 1
            a.actual_value = send

    def validate(self, spec, reporter):
        kafka = KafkaConn()
        consumed = kafka.consume(spec.topic, spec.assertions.get("timeout_after", 2.0))
        with Assertion(
            "total_events", spec.assertions, "total amount of received events", reporter
        ) as a:
            # should not be needed to keep track here
            # assertions.append(a)
            a.actual_value = len(consumed)

        with UnorderedDiffAssertion(
            "unordered", spec.assertions, "unordered events", reporter
        ) as a:
            a.actual_value = consumed

    def represent(self):
        return (
            f"BrokerKafka {self.spec.execution_mode.represent()} to {self.spec.topic}"
        )
