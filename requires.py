from charms.reactive import Endpoint
from charms.reactive.flags import toggle_flag
from charmhelpers.core.hookenv import ingress_address


'''
This interface is desiged to be compatible with a previous
implementation based on RelationBase.

The old `{endpoint_name}.available` flags are maintained
'''


class PrometheusRequires(Endpoint):
    def manage_flags(self):
        """
        Managing the availability flag based on the port field from a connected
        unit.  It is convention that remote units signal availability this way.
        """
        has_port = self.all_joined_units.received['port']
        toggle_flag(self.expand_name('endpoint.{endpoint_name}.available'),
                    has_port)
        # compatibility
        toggle_flag(self.expand_name('{endpoint_name}.available'),
                    has_port)

    def targets(self):
        """
        Interface method returns a list of available prometheus targets.
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

                # If the hostname is not provided we use the informaton from
                # the relation
                host = (unit.received['hostname'] or
                        ingress_address(relation.relation_id, unit.unit_name))
                port = unit.received['port']

                # Skipping this unit if it isn't ready yet
                if host and port:
                    service['targets'].append('{}:{}'.format(host, port))
                else:
                    continue

                if unit.received['metrics_path']:
                    service['metrics_path'] = unit.received['metrics_path']
                if unit.received['labels']:
                    service['labels'] = unit.received['labels']

                # Optional fields
                if unit.received['scrape_interval']:
                    service['scrape_interval'] = \
                            unit.received['scrape_interval']
                if unit.received['scrape_timeout']:
                    service['scrape_timeout'] = unit.received['scrape_timeout']
        return [s for s in services.values() if s['targets']]
