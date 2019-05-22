from charms.reactive import Endpoint
from charms.reactive import hook, when, when_not
from charmhelpers.core import hookenv
from charms.reactive.flags import clear_flag, set_flag


'''
This interface is desiged to be compatible with a previous
implementation based on RelationBase.

Specifically
- the `{endpoint_name}.available` flags 
- the use of `to_publish_raw` to avoid double quoting of the values 
  as the old interface used plain values here
'''


class PrometheusProvides(Endpoint):

    def configure(self, port, path='/metrics',
                  scrape_interval=None, scrape_timeout=None, labels={}):
        """
        Interface method to set information provided to remote units
        """

        # Use our unit name if the label isn't provided
        if labels.get('host') is None:
            unit_name = hookenv.local_unit()
            labels['host'] = unit_name.replace("/", "-")
        
        for relation in self.relations:
            relation.to_publish_raw['hostname'] = hookenv.ingress_address(
                relation.relation_id, hookenv.local_unit()
            )
            relation.to_publish_raw['port'] = port
            relation.to_publish_raw['metrics_path'] = path
            relation.to_publish['labels'] = labels
            if scrape_interval is not None:
                relation.to_publish_raw['scrape_interval'] = scrape_interval
            if scrape_timeout is not None:
                relation.to_publish_raw['scrape_timeout'] = scrape_timeout

    @when('endpoint.{endpoint_name}.joined')
    def available(self):
        """
        Raising the available flag when a unit joined
        """
        set_flag(self.expand_name('endpoint.{endpoint_name}.available'))
        set_flag(self.expand_name('{endpoint_name}.available')) #compatibility


    @when('endpoint.{endpoint_name}.departed')
    def broken(self):
        """
        Remove the available flag when the last unit has departed
        """
        if not self.is_joined:
            clear_flag(self.expand_name('endpoint.{endpoint_name}.available'))
            clear_flag(self.expand_name('{endpoint_name}.available')) #compatibility