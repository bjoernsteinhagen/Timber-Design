from specklepy.transports.server import ServerTransport
from specklepy.api.models import Branch
from specklepy.api.client import SpeckleClient
from specklepy.api import operations

class Project:
    def __init__(self, client : 'SpeckleClient', project_id: str, model_results_name: str):
        self.client = client
        self.project_id = project_id
        self.model_results_name = model_results_name

    def get_results_model(self):
        model: 'Branch' = self.client.branch.get(self.project_id, self.model_results_name, commits_limit = 1)
        if not model:
            self.client.branch.create(stream_id=self.project_id, name=self.model_results_name)

    def send_results_model(self, object):
        remote_transport = ServerTransport(self.project_id, self.client)
        hash = operations.send(base=object, transports=[remote_transport])
        commit_id = self.client.commit.create(self.project_id, object_id=hash, branch_name=self.model_results_name)
