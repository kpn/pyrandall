from pyrandall.kafka import KafkaConn
from pyrandall.types import Assertion

from .common import Executor


class BrokerKafka(Executor):
    def __init__(self, spec, *args, **kwargs):
        super().__init__()
        self.execution_mode = spec.execution_mode
        self.spec = spec

    def execute(self, reporter):
        # assume execution mode is producing for now (simulate test cases)
        spec = self.spec
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

    def represent(self):
        return (
            f"BrokerKafka {self.spec.execution_mode.represent()} to {self.spec.topic}"
        )
