
from constants import AS2805_DESCRIPTION

class PaymentsDirectFailure(Exception):
    def __init__(self, response, *args, **kwargs):
        super(PaymentsDirectFailure, self).__init__(*args, **kwargs)
        self.response = response

    def __str__(self):
        code = self.response.ResponseCode
        description = AS2805_DESCRIPTION.get(code, self.response.ResponseDescription)
        reference = getattr(self.response, 'BankReferenceNumber', 'Not supplied')
        return "[Errno %s] %s (ref %s)" % (code, description, reference)

