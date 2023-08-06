from django.conf import settings
from django.core.urlresolvers import reverse

class Service(object):
    
    def __init__(self, data, project, project_user, branch, build, previous_build, results):
        self.data = data
        self.project = project
        self.project_user = project_user
        self.branch = branch
        self.build = build
        self.previous_build = previous_build
        self.results = results
    
    def get_build_url(self):
        url = settings.ROOT_URL + reverse("project", args=[self.project_user["username"], self.project["url_name"]])
        url += "#%s/%d" % (self.branch["name"], self.build["display_id"])
        return url
    
    def get_service_url(self):
        url = settings.ROOT_URL + reverse("projectadmin:hooks", args=[self.project_user["username"], self.project["url_name"], self.__class__.__name__.lower()])
        return url
