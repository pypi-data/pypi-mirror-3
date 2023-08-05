from logilab.common.decorators import monkeypatch
from cubes.vcsfile import entities as vcsfile

@monkeypatch(vcsfile.Repository, 'project')
@property
def project(self):
    if self.reverse_source_repository:
        return self.reverse_source_repository[0]
    if hasattr(self, 'patchrepo_of') and self.patchrepo_of: # vcreview
        return self.patchrepo_of.project
    return None
