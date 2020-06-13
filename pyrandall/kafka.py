import configparser
import io
import logging
import os
import sys
import time
from enum import Enum
from typing import Dict

from confluent_kafka.cimpl import Consumer, KafkaError, KafkaException, Producer

log = logging.getLogger("kafka")


class ConsumerState(Enum):
    PARTITIONS_UNASSIGNED = 0
    PARTITIONS_ASSIGNED = 1
    TIMEOUT_SET = 2


class KafkaSetupError(Exception):
    pass


class KafkaConn:

    def __init__(self):
        self.consume_lock = ConsumerState.PARTITIONS_UNASSIGNED

    # callback for consumer partition assignment,
    # removes lock for actual consumption
    def callback_on_assignment(self, consumer, partitions):
        self.consume_lock = ConsumerState.PARTITIONS_ASSIGNED
        offsets = consumer.committed(partitions)
        log.info(f"Assignment: {offsets}")

    def check_connection(self):
        def check_callback(error, event):
            if error:
                if error.code() == KafkaError._MSG_TIMED_OUT:
                    log.error(
                        "This Timout might indicate the broker is down or connection is misconfigured"
                    )
                log.error(f"Error while producing initial msg: {error}")
                raise KafkaSetupError()

        config = ConfigFactory(kafka_client="producer").config
        config["delivery.timeout.ms"] = "3000"  # 3 seconds
        prod = Producer(config)
        prod.produce("pyrandall", "starting simulate", callback=check_callback)
        prod.flush()  # block until callback is called

    def prod_reporter(self, error, event):
        if error:
            log.error(f"Error producing the event: {error}")
        else:
            log.info(
                f"Event produced, topic: {event.topic()}, \
                    partition: {event.partition()}"
            )

    def produce_message(self, topic, body, headers=None, partition_key=None):
        if headers is None:
            msg_headers = {}
        self._produce(topic, body, partition_key, msg_headers)
        self.producer.flush()

    def init_producer(self):
        log.info("starting produce")
        kafka_config_producer = ConfigFactory(kafka_client="producer")
        config = kafka_config_producer.config
        log.info("kafka config for produce %s", config)

        self.check_connection()
        self.producer = Producer(config)

    def _produce(self, topic, msg, partition_key=None, headers=None):
        try:
            if partition_key:
                self.producer.produce(
                    topic, msg, key=partition_key, callback=self.prod_reporter
                )
            else:
                self.producer.produce(topic, msg, callback=self.prod_reporter)
            print(".", end="")
        except BufferError:
            log.error(
                "%% Local producer queue is full (%d messages \
                        awaiting delivery): try again",
                len(self.producer),
            )

    # The consume function now contains a lock, the lock is removed when the
    # partitions are assigned (max 60 seconds). After assignment the regular
    # timeout are used. These should be set to a couple of seconds in the
    # scenario itself                      .
    def consume(self, topic, topic_timeout):
        kafka_config_consumer = ConfigFactory(kafka_client="consumer")
        config = kafka_config_consumer.config
        log.info("kafka config for consume %s", config)
        consumer = Consumer(config)

        events = []

        start_time = time.monotonic()
        timeout_start_time = start_time
        timeout_consumer = 10.0

        # actual consumer starts now
        # subscribe to 1 or more topics and define the callback function
        # callback is only received after consumer.consume() is called!
        consumer.subscribe([topic], on_assign=self.callback_on_assignment)
        log.info(f"Waiting for partition assignment ... (timeout at {timeout_consumer} seconds")
        try:
            while (time.monotonic() - timeout_start_time) < timeout_consumer:
                # start consumption
                messages = consumer.consume(timeout=0.1)
                # check for partition assignment
                if self.consume_lock == ConsumerState.PARTITIONS_UNASSIGNED:
                    # this should not happen but we are not 100% sure
                    if messages:
                        log.error("messages consumed but lock is unopened")
                        break
                    continue
                # after partition assignment set the timeout again
                # and reset the start time from which to determine timeout
                # violation
                elif self.consume_lock == ConsumerState.PARTITIONS_ASSIGNED:
                    
                    timeout_start_time = time.monotonic()
                    timeout_consumer = topic_timeout

                    self.consume_lock = ConsumerState.TIMEOUT_SET
                    log.info("Lock has been opened, consuming ...")

                # appened messages to the events list to be returned
                if messages:
                    for msg in messages:
                        log.info(
                            f"message at offset: {msg.offset()}, \
                                partition: {msg.partition()}, \
                                topic: {msg.topic()}"
                        )
                        # TODO: allow assertions to be on message headers etc.
                        # events.append({
                        #     "key": msg.key,
                        #     "headers": msg.headers,
                        #     "value": msg.value()
                        # })
                        events.append(msg.value())
            # only executed when while condition becomes false
            else:
                # at the end check if the partition assignment was achieved
                if self.consume_lock != ConsumerState.TIMEOUT_SET:
                    log.error("No partition assignments received in time")

        except KafkaException as e:
            log.error(f"Kafka error: {e}")
            pass

        finally:
            consumer.close()

        end_time = time.monotonic()
        log.debug(f"this cycle took: {(end_time - start_time)} seconds")

        return events


class ConfigFactory:
    def __init__(self, kafka_client=None, fpath=None):
        self.config = {}
        kafka_properties = os.environ.get("KAFKA_PROPERTIES")
        if fpath is not None:
            # print("fpath")
            self.config = self.from_properties(fpath)
        elif kafka_properties:
            # print("kafka_properties")
            self.config = self.from_properties(kafka_properties)
        else:
            # print("from_env")
            self.config = self.from_env()
        if kafka_client == "consumer":
            self.config["group.id"] = "pyrandall-test"
            self.config["auto.offset.reset"] = "earliest"
            # self.config['debug'] = "topic,msg,broker"
            self.config["enable.partition.eof"] = "false"
        elif kafka_client == "producer":
            # self.config['debug'] = "topic,msg,broker"
            self.config["max.in.flight.requests.per.connection"] = 1
            self.config["enable.idempotence"] = True
            self.config["retries"] = 1
            self.config["delivery.timeout.ms"] = "30000"  # 30 seconds
            pass

    @staticmethod
    def from_env() -> Dict[str, str]:
        config = {}
        broker = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        config["bootstrap.servers"] = broker
        return config

    @staticmethod
    def from_properties(fpath) -> Dict[str, str]:
        section = "root"
        with open(fpath) as f:
            ini_str = io.StringIO(f"[{section}]\n" + f.read())

        parser = configparser.ConfigParser()
        parser.read_file(ini_str, "strioIO")
        # check parsing was done correctly
        assert parser.sections() == [section]
        return dict(parser.items(section))
