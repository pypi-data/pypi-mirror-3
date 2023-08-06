from nose import tools

from wtforms.form import Form

from wtfrecaptcha.fields import RecaptchaField
from wtfrecaptcha.validators import Recaptcha


# A group of validator subclasses that emulate calls to reCaptcha API
class RecaptchaSuccessfulValidatorMockup(Recaptcha):

    def _call_verify(self, params):
        return ('true',)

class RecaptchaFailedValidatorMockup(Recaptcha):

    def _call_verify(self, params):
        return ('false', 'incorrect-captcha-sol')

class RecaptchaInternalFailedValidatorMockup(Recaptcha):

    def _call_verify(self, params):
        return ('false', 'invalid-request-cookie')

class RequestDictMock(dict):
    """Emulates multidict-like behaviour"""

    def getall(self, key):
        data = []
        if self.has_key(key):
            data.append(self[key])
        return data


class TestRecaptcha(object):

    captcha_data = RequestDictMock({
            'recaptcha_challenge_field': 'testchallenge',
            'recaptcha_response_field': 'testresponse'
    })

    @tools.raises(ValueError)
    def test_missing_keys(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField()

        form = CaptchaForm()

    def test_insecure_form_widget(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField(public_key='testpub',
                    private_key='testpriv')

        form = CaptchaForm()
        insecure_widget =u"""<script type="text/javascript"
 src="http://www.google.com/recaptcha/api/challenge?k=testpub">
</script>
<noscript>
 <iframe src="http://www.google.com/recaptcha/api/noscript?k=testpub"
     height="300" width="500" frameborder="0"></iframe><br>
 <textarea name="recaptcha_challenge_field" rows="3" cols="40">
 </textarea>
 <input type="hidden" name="recaptcha_response_field"
     value="manual_challenge">
</noscript>"""

        tools.assert_equal(unicode(form.captcha), insecure_widget)

    def test_secure_form_widget(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField(public_key='testpub',
                    private_key='testpriv', secure=True)

        form = CaptchaForm()
        secure_widget = u"""<script type="text/javascript"
 src="https://www.google.com/recaptcha/api/challenge?k=testpub">
</script>
<noscript>
 <iframe src="https://www.google.com/recaptcha/api/noscript?k=testpub"
     height="300" width="500" frameborder="0"></iframe><br>
 <textarea name="recaptcha_challenge_field" rows="3" cols="40">
 </textarea>
 <input type="hidden" name="recaptcha_response_field"
     value="manual_challenge">
</noscript>"""

        tools.assert_equal(unicode(form.captcha), secure_widget)

    @tools.raises(ValueError)
    def test_missing_data(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField(public_key='testpub',
                    private_key='testpriv')

        form = CaptchaForm(RequestDictMock())

    def test_missing_challenge(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField(public_key='testpub',
                    private_key='testpriv')

        form = CaptchaForm(RequestDictMock(
            {'recaptcha_response_field': 'testresponse'}),
            captcha={'ip_address': '127.0.0.1'})
        assert form.validate() == False, 'Form validates'
        tools.assert_not_equal(form.errors.get('captcha'), None)

    @tools.nottest
    def _check_validator(self, form, error_text):
        """Helper for common validator checks"""
        assert form.validate() == False, 'Form validates'
        captcha_error = form.errors.get('captcha')
        tools.assert_not_equal(captcha_error, None)
        tools.assert_equal(captcha_error[0], error_text)

    def test_missing_response(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField(public_key='testpub',
                    private_key='testpriv')

        form = CaptchaForm(RequestDictMock(
            {'recaptcha_challenge_field': 'testchallenge'}),
            captcha={'ip_address': '127.0.0.1'})
        self._check_validator(form, Recaptcha.empty_error_text)

    def test_incorrect_solution(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField(public_key='testpub',
                    private_key='testpriv',
                    validators = [RecaptchaFailedValidatorMockup()])

        form = CaptchaForm(self.captcha_data, captcha={'ip_address': '127.0.0.1'})
        self._check_validator(form, Recaptcha.errors['incorrect-captcha-sol'])

    def test_internal_error(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField(public_key='testpub',
                    private_key='testpriv',
                    validators = [RecaptchaInternalFailedValidatorMockup()])

        form = CaptchaForm(self.captcha_data, captcha={'ip_address': '127.0.0.1'})
        self._check_validator(form, Recaptcha.internal_error_text)

    def test_solved_captcha(self):
        class CaptchaForm(Form):
            captcha = RecaptchaField(public_key='testpub',
                    private_key='testpriv',
                    validators = [RecaptchaSuccessfulValidatorMockup()])

        form = CaptchaForm(self.captcha_data, captcha={'ip_address': '127.0.0.1'})
        assert form.validate() == True, 'Form does not validate'

