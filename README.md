# PYRANDALL

Simulator and Sanitytest framework that encourages to write tests upfront, but are suitable to run as e2e tests.
The framework has a focus on supporting Event Streaming and Stream Processors.

## Running examples

```
# setup a venv and start mocks to
docker-compose up -d
pip install flask
python stubserver.py
```

```
# Simulate events from examples/scenarios/v2.yaml and files found in examples/events
./examples/pyrandall simulate v2.yaml
```

```
# Validate results from examples/scenarios/v2.yaml and files found in examples/results
./examples/pyrandall validate v2.yaml
```

# Example of scenario/v2 schema

The input yaml is validated with jsonschema, found here `pyrandall/schemas/scenario/v2.yaml`

```
---
version: scenario/v2
feature:
  description: V2 schema example
  scenarios:
    - description: HTTP to an ingest API and key-value API
      simulate:
        adapter: requests/http
        requests:
          - path: /v1/actions/produce-event
            events:
              - words1.json
              - words2.json
      validate:
        adapter: requests/http
        requests:
          - path: /foo/bar/123
            assert_that_responded:
              status_code: { equals_to: 200 }
              body: { equals_to_event: expected_result.json }
    - description: Produce and Consumer to kafka
      simulate:
        adapter: broker/kafka
        messages:
          - topic: emails
            events:
              - email1.json
      validate:
        adapter: broker/kafka
        messages:
          - topic: email_results
            assert_that_received:
              timeout_after: "5m"
              total_events: { equals_to: 4 } # I observed in total 4 events
              unordered:
                - { equals_to_event: word_count.json }
          - topic: email_results
            assert_that_received:
              last_event: { equals_to_event: word_count.json }
              timeout_after: 5m
```


## Features and Ideas

* Runnable pyrandall command to execute a BDD style scenario spec in YAML.
* Focus on developers experience when creating dataflows. Where the emphasis lies in creating the events.
* Simulated "events" are read from template files. By default json is supported.
* Possibility to overwrite or extend pyrandall default behaviors with pluggy, a plugin system developed and used by pytest.
* See a complete example of the pluggy: [https://pluggy.readthedocs.io/en/latest/#a-complete-example](https://pluggy.readthedocs.io/en/latest/#a-complete-example)


Pyrandall is run from within docker. Connections are often only accessible through deployment and containers are de facto today.
It also enables us to add complex dependencies like `librdkafka` to use confluent-kafka which supports all api versions offered by Kafka.

For adding plugins, self signed certificates etc, it is encouraged to create your own Dockerfile:

```{Dockerfile}
FROM kpnnv/pyrandall:latest

# Install your plugins
# COPY certificates etc
```

## Concepts

* A spec can consist of multiple simulate and validate steps which are executed over HTTP or Apache Kafka.
* This could be expanded to brokers in general or websockets support.
* Validate should executes assertions on the outputs of your application.


## Documentation

Pyrandall always could use more documentation, and help is welcome see our CONTRIBUTING.md.
At this moment code and tests are the best we have. See the `examples/` and the `test/functional`.
Also see `CHANGELOG.md` on what is fixed, changed or added.


# License


```
Copyright 2019 KPN N.V.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
