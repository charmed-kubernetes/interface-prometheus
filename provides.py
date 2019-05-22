from charms.reactive import Endpoint
from charms.reactive import hook, when, when_not
from charmhelpers.core import hookenv
from charms.reactive.flags import clear_flag, set_flag


class PrometheusProvides(Endpoint):

    def configure(self, port, path='/metrics',
                  scrape_interval=None, scrape_timeout=None, labels={}):
        unit_name = hookenv.local_unit()
        if labels.get('host') is None:
            labels['host'] = unit_name.replace("/", "-")
        
        for relation in self.relations:
            relation.to_publish_raw['hostname'] = hookenv.unit_private_ip()
            relation.to_publish_raw['port'] = port
            relation.to_publish_raw['metrics_path'] = path
            relation.to_publish['labels'] = labels
            if scrape_interval is not None:
                relation.to_publish_raw['scrape_interval'] = scrape_interval
            if scrape_timeout is not None:
                relation.to_publish_raw['scrape_timeout'] = scrape_timeout

    @when('endpoint.{endpoint_name}.departed')
    def broken(self):
        if not self.is_joined:
            clear_flag(self.expand_name('endpoint.{endpoint_name}.available'))

    @when('endpoint.{endpoint_name}.joined')
    def available(self):
        if self.is_joined:
            set_flag(self.expand_name('endpoint.{endpoint_name}.available'))

