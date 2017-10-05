from charms.reactive import RelationBase, scopes, hook
from charmhelpers.core import hookenv


class PrometheusProvides(RelationBase):
    scope = scopes.UNIT

    @hook('{provides:prometheus}-relation-{joined,changed}')
    def changed(self):
        self.set_state('{relation_name}.available')

    @hook('{provides:prometheus}-relation-{broken,departed}')
    def broken(self):
        self.remove_state('{relation_name}.available')

    def configure(self, port, path='/metrics',
                  scrape_interval=None, scrape_timeout=None, labels={}):
        unit_name = hookenv.local_unit()
        if labels.get('host') is None:
            labels['host'] = unit_name.replace("/", "-")
        relation_info = {
            'hostname': hookenv.unit_private_ip(),
            'port': port,
            'metrics_path': path,
            'labels': labels,
        }
        if scrape_interval is not None:
            relation_info['scrape_interval'] = scrape_interval
        if scrape_timeout is not None:
            relation_info['scrape_timeout'] = scrape_timeout
        self.set_remote(**relation_info)
