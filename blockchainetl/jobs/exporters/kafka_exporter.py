import collections
import json
import logging

from kafka import KafkaProducer

from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter


class KafkaItemExporter:
    # TODO: Add support for multiple broker endpoints
    def __init__(self, output, item_type_to_topic_mapping, converters=()):
        self.item_type_to_topic_mapping = item_type_to_topic_mapping
        self.converter = CompositeItemConverter(converters)
        self.connection_urls = self.get_connection_url(output)
        if self.connection_urls is not None:
            print(self.connection_urls)
            self.producer = KafkaProducer(bootstrap_servers=self.connection_urls)
        else:
            raise Exception('Invalid ')

    def get_connection_url(self, output):
        servers = []
        try:
            for endpoint in output.split('/')[1].split(';'):
                servers.append(endpoint)
        except Exception as e:
            raise Exception('Invalid kafka output param, It should be in format of "kafka/127.0.0.1:9092;122.0.0.1:9092"')
        return servers if len(servers) > 0 else None

    def open(self):
        pass

    def export_items(self, items):
        for item in items:
            self.export_item(item)

    def export_item(self, item):
        item_type = item.get('type')
        if item_type is not None and item_type in self.item_type_to_topic_mapping:
            data = json.dumps(item).encode('utf-8')
            logging.debug(data)
            return self.producer.send(self.item_type_to_topic_mapping[item_type], value=data)
        else:
            logging.warning('Topic for item type "{}" is not configured.'.format(item_type))

    def convert_items(self, items):
        for item in items:
            yield self.converter.convert_item(item)

    def close(self):
        pass


def group_by_item_type(items):
    result = collections.defaultdict(list)
    for item in items:
        result[item.get('type')].append(item)

    return result
