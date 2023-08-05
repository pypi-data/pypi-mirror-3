from blazeweb.globals import settings
from blazeweb.views import SecureView
from werkzeug.exceptions import NotFound, BadRequest
import actions
import difflib
import re

class AuditDiffBase(SecureView):
    def init(self):
        self.extend_from = settings.template.default
        self.pagetitle = 'Change History'
        self.ident_mask = None

    def auth_calculate(self, rev1, rev2=None):
        SecureView.auth_calculate(self)
        self.ar = actions.audit_record_get(rev1)
        if not self.ar:
            raise NotFound
        if not re.match(self.ident_mask, self.ar.identifier):
            raise BadRequest

    def default(self, rev1, rev2=None):
        prev_ar = actions.audit_record_get(rev2) if rev2 else actions.get_previous_audit_record(rev1)

        diff_text = []
        a = prev_ar.audit_text.splitlines(True) if prev_ar else []
        b = self.ar.audit_text.splitlines(True)
        diff = difflib.SequenceMatcher(None, a, b)
        # op is tuple: (opcode, prev_ar_begin, prev_ar_end, ar_begin, ar_end)
        for op in diff.get_opcodes():
            if op[0] == "replace":
                diff_text.append('<del class="audit">'+''.join(a[op[1]:op[2]]) + '</del><ins class="audit">'+''.join(b[op[3]:op[4]])+"</ins>")
            elif op[0] == "delete":
                diff_text.append('<del class="audit">'+ ''.join(a[op[1]:op[2]]) + "</del>")
            elif op[0] == "insert":
                diff_text.append('<ins class="audit">'+''.join(b[op[3]:op[4]]) + "</ins>")
            elif op[0] == "equal":
                diff_text.append(''.join(b[op[3]:op[4]]))

        self.assign('diff_text', ''.join(diff_text))
        self.assign('extend_from', self.extend_from)
        self.assign('pagetitle', self.pagetitle)
        self.assign('old_rev_ts', prev_ar.createdts if prev_ar else None)
        self.assign('new_rev_ts', self.ar.createdts)
        self.render_endpoint('audit:audit_diff.html')
