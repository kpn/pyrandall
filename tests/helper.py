import os
import shlex
import subprocess
import time

from confluent_kafka import Consumer, Producer, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic

bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def shelldon(command: str, stderr=False):
    cmd = shlex.split(command)
    if stderr:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE)

    stdout = ""
    if proc.stdout:
        stdout = proc.stdout.decode("utf-8")

    stderr = ""
    if proc.stderr:
        stderr = proc.stderr.decode("utf-8")

    return (proc.returncode, stdout, stderr)


def ensure_topic(topicname):
    # use this over admin client to ensure docker-compose file works
    client = AdminClient({"bootstrap.servers": bootstrap_servers})
    metadata = client.list_topics()
    if topicname not in metadata.topics:
        results = client.create_topics([NewTopic(topic=topicname, num_partitions=1, replication_factor=1)])
        future = results[topicname]
        future.result()


class KafkaProducer(Producer):
    def __init__(self, topic):
        ensure_topic(topic)
        self.topic = topic
        super().__init__({"bootstrap.servers": bootstrap_servers})

    def send(self, message):
        self.produce(self.topic, message)
        self.flush()


class KafkaConsumer(Consumer):
    def __init__(self, topicname):
        # ensure_topic(topicname)
        super().__init__({"group.id": "pyrandall-pytest", "bootstrap.servers": bootstrap_servers})
        self.waiting_assignment = True
        self.topic = topicname
        self.topic_partition = TopicPartition(topic=self.topic, partition=0)
        # open connection with kafka and do not rely on latest offset.
        # because latest offset is retrieved on partition assignment
        # that would happen after the messages in our functional tests are produced
        self.goto_largest_offset()
        self.subscribe([topicname], self.on_assign)

    def goto_largest_offset(self):
        offset = self.get_high_watermark()
        self.commit(
            offsets=[TopicPartition(topic=self.topic, partition=0, offset=offset)]
        )

    def on_assign(self, consumer, partitions):
        print("partition assignment callbacked called")
        self.waiting_assignment = False

    def get_one_message(self):
        waiting = 0.0
        while waiting <= 10.0:
            messages = self.consume(timeout=0.1)
            time.sleep(0.4)
            waiting += 0.5
            if not messages or self.waiting_assignment:
                continue
            else:
                return messages
        assert not self.waiting_assignment, "should not timeout on partition assignment"
        print(f"total time until assignment: {waiting} in seconds")
        return []

    def get_messages(self, expecting):
        waiting = 0.0
        out = []
        while waiting <= 10.0:
            messages = self.consume(timeout=0.1)
            time.sleep(0.4)
            waiting += 0.5
            if not messages or self.waiting_assignment:
                continue
            else:
                out += messages

            if expecting == len(out):
                break

        assert not self.waiting_assignment, "should not timeout on partition assignment"
        print(f"total time until assignment: {waiting} in seconds")
        return out

    def get_high_watermark(self):
        res = self.get_watermark_offsets(self.topic_partition)
        assert res
        _, high_watermark = res
        # if high_watermark > 1:
        #     current_offset = high_watermark - 1
        return high_watermark
