from docar import Document, Collection
from docar import fields
from docar.backends.http import HttpBackendManager

from libthirty.state import construct_resource_uri
from libthirty.validators import resource_name

import os


HttpBackendManager.SSL_CERT = os.path.join(
        os.path.dirname(__file__), "ssl", "StartSSL_CA.pem")

class User(Document):
    username = fields.StringField()
    email = fields.StringField()
    is_active = fields.BooleanField()


class Account(Document):
    name = fields.StringField()
    #users = fields.CollectionField(User)

    class Meta:
        backend_type = 'http'
        identifier = 'name'


class CnameRecord(Document):
    record = fields.StringField()

    class Meta:
        backend_type = 'http'
        identifier = 'record'


class CnameRecords(Collection):
    document = CnameRecord

    def _render(self):
        data = []
        for doc in self.collection_set:
            #doc.fetch()
            item = {
                    "record": doc.record,
                    }
            data.append(item)

        return data


class Backend(Document):
    region = fields.StringField(default="eu1")
    count = fields.NumberField(default=1)
    dns_record = fields.StringField(optional=True)

    class Meta:
        backend_type = 'http'
        identifier = 'region'


class BackendCollection(Collection):
    document = Backend

    def _render(self):
        data = []
        for doc in self.collection_set:
            #doc.fetch()
            item = {
                    "region": doc.region,
                    "count": doc.count
                    }
            data.append(item)

        return data


class Database(Document):
    name = fields.StringField(validators=[])
    label = fields.StaticField(value="database")
    variant = fields.StringField(default="postgresql")
    username = fields.StringField()
    password = fields.StringField()
    host = fields.StringField()
    port = fields.NumberField()

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def uri(self):
        return construct_resource_uri(label='database', resource=self.name,
                environment=None)


class Repository(Document):
    name = fields.StringField(validators=[resource_name])
    label = fields.StaticField(value="repository")
    variant = fields.StringField(default='git')
    location = fields.StringField()
    # username = fields.StringField(optional=True)
    # password = fields.StringField(optional=True)
    ssh_key = fields.StringField(optional=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def save_variant_field(self):
        return 0

    def render_variant_field(self, value):
        return "git"

    def uri(self):
        return construct_resource_uri(label='repository', resource=self.name,
                environment=None)

    def post_uri(self):
        return construct_resource_uri(label='repository', resource=None)


class Webserver(Document):
    name = fields.StringField(validators=[resource_name])
    label = fields.StaticField(value="webserver")
    variant = fields.StringField(default='nginx')

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def uri(self):
        return construct_resource_uri(label='webserver', resource=self.name,
                environment=None)


class WsgiAppFlavor(Document):
    id = fields.NumberField(scaffold=False, optional=True, render=False)
    wsgi_entrypoint = fields.StringField()

    class Meta:
        backend_type = 'http'
        context = []

    def to_python(self):
        return self._prepare_render()


class DjangoAppFlavor(Document):
    id = fields.NumberField(scaffold=False, optional=True, render=False)
    django_settings_module = fields.StringField(default="settings")
    inject_db = fields.BooleanField(default=True)

    class Meta:
        backend_type = 'http'
        context = []

    def to_python(self):
        return self._render()


class PythonEnvironment(Document):
    name = fields.StringField(validators=[resource_name])
    database = fields.ForeignDocument(Database, optional=True, scaffold=False)
    #webserver = fields.ForeignDocument(Webserver)

    project_root = fields.StringField(default="")
    repo_commit = fields.StringField(default='HEAD')
    repo_branch = fields.StringField(default="master")
    install_setup_py = fields.BooleanField(default=False)
    requirements_file = fields.StringField(default="requirements",
            optional=True)
    flavor = fields.StringField(default="wsgi")

    backends = fields.CollectionField(BackendCollection, inline=True)
    wsgiflavor = fields.ForeignDocument(WsgiAppFlavor, optional=True,
            inline=True)
    djangoflavor = fields.ForeignDocument(DjangoAppFlavor, optional=True,
            inline=True)
    cname_records = fields.CollectionField(CnameRecords, inline=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['app']

    def uri(self):
        return construct_resource_uri(label='app', environment=self.name)

    def post_uri(self):
        return "%senvironment/" % construct_resource_uri(label="app",
                environment=None)


class PythonEnvCollection(Collection):
    document = PythonEnvironment


class App(Document):
    name = fields.StringField(validators=[resource_name])
    label = fields.StaticField(value="app")
    variant = fields.StringField(default='python')
    repository = fields.ForeignDocument(Repository)
    environments = fields.CollectionField(PythonEnvCollection)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def save_variant_field(self):
        return 1

    def render_variant_field(self, value):
        return "python"

    def post_uri(self):
        return construct_resource_uri(label='app', resource=None)

    def uri(self):
        return construct_resource_uri(label='app', resource=self.name,
                environment=None)
