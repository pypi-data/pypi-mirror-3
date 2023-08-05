from blazeweb.routing import url_for
from webhelpers.html.tags import link_to

from compstack.datagrid.lib import Table, Col, Link, DateTime, Links, A
import actions

def audit_record_display(identifier, diff_view):
    t = Table(class_='datagrid')
    t.createdts = DateTime('Date', format='%m/%d/%Y %H:%M:%S', width_th='20%')
    t.user_id = Col('User', extractor=lambda x: (('%s %s' % (x.user.name_first or '', x.user.name_last or '')).strip() or x.user.login_id) if x.user else 'no user', width_th='20%')
    t.comments = Col('Comments')
    t.diff = Col('Diff', extractor=lambda x: link_to('Diff', url_for(diff_view, rev1=x.id)))
    return t.render(actions.get_audit_record_list(identifier))