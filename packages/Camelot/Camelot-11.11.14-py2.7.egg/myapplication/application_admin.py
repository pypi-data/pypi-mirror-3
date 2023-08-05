
from camelot.view.art import Icon
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section

class MyApplicationAdmin(ApplicationAdmin):
  
    name = 'My Application'
    application_url = 'http://www.python-camelot.com'
    help_url = 'http://www.python-camelot.com/docs.html'
    author = 'My Company'
    domain = 'mydomain.com'
    
    def get_sections(self):
        from camelot.model.memento import Memento
        from camelot.model.authentication import Person, Organization
        from camelot.model.i18n import Translation
        return [Section('relation',
                        Icon('tango/22x22/apps/system-users.png'),
                        items = [Person, Organization]),
                Section('configuration',
                        Icon('tango/22x22/categories/preferences-system.png'),
                        items = [Memento, Translation])
                ]
    