from docar import Document, Collection
from docar import fields
from docar.backends.http import HttpBackendManager

from libthirty.state import resource_uri, resource_collection_uri
from libthirty.validators import naming, max_25_chars, naming_with_dashes

import os


HttpBackendManager.SSL_CERT = os.path.join(
        os.path.dirname(__file__), "ssl", "StartSSL_CA.pem")

class User(Document):
    username = fields.StringField(validators=[naming, max_25_chars])
    email = fields.StringField()
    is_active = fields.BooleanField()


class Account(Document):
    name = fields.StringField(validators=[naming, max_25_chars])
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
            item = {
                    "record": doc.record,
                    }
            data.append(item)

        return data


class Database(Document):
    name = fields.StringField(validators=[naming_with_dashes, max_25_chars])
    label = fields.StaticField(value="database")
    variant = fields.ChoicesField(choices=['postgres'], default="postgres")
    username = fields.StringField(optional=True, read_only=True)
    password = fields.StringField(optional=True, read_only=True)
    host = fields.StringField(optional=True, read_only=True)
    port = fields.NumberField(optional=True, read_only=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def uri(self):
        return resource_uri(label='database', resource=self.name)


class DatabaseCollection(Collection):
    document = Database

    def uri(self):
        return resource_collection_uri(label='database')


class Mongodb(Document):
    name = fields.StringField(validators=[naming_with_dashes, max_25_chars])
    label = fields.StaticField(value="mongodb")
    variant = fields.ChoicesField(choices=['16MB'], default='16MB')
    username = fields.StringField(optional=True, read_only=True)
    password = fields.StringField(optional=True, read_only=True)
    host = fields.StringField(optional=True, read_only=True)
    port = fields.NumberField(optional=True, read_only=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def uri(self):
        return resource_uri(label='mongodb', resource=self.name)

    def post_uri(self):
        return resource_uri(label='mongodb', resource=None)

class MongodbCollection(Collection):
    document = Mongodb

    def uri(self):
        return resource_collection_uri(label='mongodb')


class Repository(Document):
    name = fields.StringField(validators=[naming, max_25_chars])
    label = fields.StaticField(value="repository")
    variant = fields.ChoicesField(choices=['git'], default='git')
    location = fields.StringField()
    ssh_key = fields.StringField(optional=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def uri(self):
        return resource_uri(label='repository', resource=self.name)

    def post_uri(self):
        return resource_uri(label='repository', resource=None)


class RepositoryCollection(Collection):
    document = Repository

    def uri(self):
        return resource_collection_uri(label='repository')


class Worker(Document):
    name = fields.StringField(validators=[naming, max_25_chars])
    label = fields.StaticField(value="worker")
    variant = fields.ChoicesField(choices=['python'], default='python')
    instances = fields.NumberField(default=1)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def post_uri(self):
        return resource_uri(label='worker', resource=None)

    def uri(self):
        return resource_uri(label='worker', resource=self.name)


class WorkerCollection(Collection):
    document = Worker

    def uri(self):
        return resource_collection_uri(label='worker')


class App(Document):
    name = fields.StringField(validators=[naming, max_25_chars])
    label = fields.StaticField(value="app")
    variant = fields.ChoicesField(default='python',
            choices=['static', 'python'])
    repository = fields.ForeignDocument(Repository)
    database = fields.ForeignDocument(Database, optional=True)
    mongodb = fields.ForeignDocument(Mongodb, optional=True)
    worker = fields.ForeignDocument(Worker, optional=True)
    repo_commit = fields.StringField(default='HEAD')
    #repo_branch = fields.StringField(default="master")
    region = fields.StringField(default="ams1")
    instances = fields.NumberField(default=1)
    dns_record = fields.StringField(optional=True)
    cnames = fields.CollectionField(CnameRecords, inline=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def post_uri(self):
        return resource_uri(label='app', resource=None)

    def uri(self):
        return resource_uri(label='app', resource=self.name)


class AppCollection(Collection):
    document = App

    def uri(self):
        return resource_collection_uri(label='app')
