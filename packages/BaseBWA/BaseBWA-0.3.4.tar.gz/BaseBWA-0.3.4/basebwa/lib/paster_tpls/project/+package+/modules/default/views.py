from blazeweb import appimportauto
appimportauto('base', ['PublicPageView'])

class Index(PublicPageView):
    def default(self):
        pass
