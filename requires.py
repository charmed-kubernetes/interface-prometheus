from charms.reactive import Endpoint
from charms.reactive import hook, when, when_not
from charms.reactive.flags import clear_flag, set_flag
from charmhelpers.core.hookenv import service_name


class PrometheusRequires(Endpoint):

    @when('endpoint.{endpoint_name}.changed')
    def changed(self):
        if self.all_joined_units.received['port']:
            set_flag(self.expand_name('endpoint.{endpoint_name}.available'))
    

    @when('endpoint.{endpoint_name}.departed')
    def broken(self):
        if not self.is_joined:
            clear_flag(self.expand_name('endpoint.{endpoint_name}.available'))


    def targets(self):
        """
        Returns a list of available prometheus targets.
            [
                {
                    'job_name': name_of_job,
                    'targets': [ host_address:host_port, ... ],
                    'metrics_path': path_to_metrics_endpoint(optional),
                    'scrape_interval': scrape_interval(optional),
                    'scrape_timeout': scrape_timeout(optional),
                    'labels': { "label": "value", ... },
                },
                # ...
            ]
        """
        services = {}
        for relation in self.relations:
            service_name = relation.application_name
            for unit in relation.units:
                service = services.setdefault(service_name, {
                    'job_name': service_name,
                    'targets': [],
                })
                host = unit.received['hostname'] or\
                    unit.received['private-address']
                port = unit.received['port']
                if host and port:
                    service['targets'].append('{}:{}'.format(host, port))
                if unit.received['metrics_path']:
                    service['metrics_path'] = unit.received['metrics_path']
                if unit.received['scrape_interval']:
                    service['scrape_interval'] = unit.received['scrape_interval']
                if unit.received['scrape_timeout']:
                    service['scrape_timeout'] = unit.received['scrape_timeout']
                if unit.received['labels']:
                    service['labels'] = unit.received['labels']
        return [s for s in services.values() if s['targets']]

