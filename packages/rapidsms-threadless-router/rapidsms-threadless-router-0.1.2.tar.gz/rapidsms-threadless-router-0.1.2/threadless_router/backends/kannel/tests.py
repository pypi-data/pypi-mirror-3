from django.conf import settings
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from threadless_router.backends.kannel import views


class HttpTest(TestCase):

    urls = 'threadless_router.backends.kannel.urls'

    def setUp(self):
        self.rf = RequestFactory()
        self.url = reverse('kannel-backend', args=['kannel-backend'])
        self.conf = {}
        self.view = views.KannelBackendView.as_view(conf=self.conf)

    def _get(self, data={}):
        request = self.rf.get(self.url, data)
        return self.view(request, backend_name='kannel-backend')

    def test_valid_form(self):
        """ Form should be valid if GET keys match configuration """
        view = views.KannelBackendView(conf=self.conf)
        data = {'id': '1112223333', 'text': 'hi there'}
        view.request = self.rf.get(self.url, data)
        form = view.get_form(view.get_form_class())
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """ Form is invalid if POST keys don't match configuration """
        view = views.KannelBackendView(conf=self.conf)
        data = {'invalid-phone': '1112223333', 'invalid-message': 'hi there'}
        view.request = self.rf.get(self.url, data)
        form = view.get_form(view.get_form_class())
        self.assertFalse(form.is_valid())

    def test_invalid_response(self):
        """ HTTP 400 should return if form is invalid """
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self._get(data)
        self.assertEqual(response.status_code, 400)
