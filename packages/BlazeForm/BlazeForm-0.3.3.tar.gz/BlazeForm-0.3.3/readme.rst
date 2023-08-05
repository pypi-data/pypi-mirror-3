Introduction
---------------

BlazeForm is a library designed to facilitate the rendering/processing/validating
of HTML forms.

Features
---------------
- validation based on FormEncode
- attempting to have complete HTML spec coverage
- extensible rendering system() (don't have to use it)
- will work with multiple WSGI frameworks (Werkzeug currently supported)
- *extensive* unit tests
- few dependencies: FormEncode, BlazeUtils, WebHelpers

Code Sample
--------------------

Using it might look like this::

    class MyForm(Form):
        def __init__(self):
            Form.__init__(self, 'myform')

            el = self.els.add_header('input-els', 'Optional Elements')
            el = self.els.add_button('button', 'Button', defaultval='PushMe')
            el = self.els.add_checkbox('checkbox', 'Checkbox')
            el = self.els.add_file('file', 'File')
            el = self.els.add_hidden('hidden', defaultval='my hidden val')
            el = self.els.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
            el = self.els.add_text('text', 'Text')
            el.add_note('a note')
            el.add_note('an <strong>HTML</strong> note', False)
            el = self.els.add_text('nolabel', defaultval='No Label')
            el.add_note('a note')
            el = self.els.add_password('password', 'Password')
            el = self.els.add_confirm('confirm', 'Confirm Password', match='password')
            el.add_note('confirm characters for password field are automatically masked')
            el = self.els.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
            el.add_note('note the automatic conversion from datetime object')
            emel = self.els.add_email('email', 'Email')
            el = self.els.add_confirm('confirmeml', 'Confirm Email', match=emel)
            el.add_note('note you can confirm with the name of the field or the element object')
            el.add_note('when not confirming password field, characters are not masked')
            el = self.els.add_time('time', 'Time')
            el = self.els.add_url('url', 'URL')
            options = [('1', 'one'), ('2','two')]
            el = self.els.add_select('select', options, 'Select')
            el = self.els.add_mselect('mselect', options, 'Multi Select')
            el = self.els.add_textarea('textarea', 'Text Area')
            el = self.els.add_fixed('fixed', 'Fixed', 'fixed val')
            el = self.els.add_fixed('fixed-no-label', defaultval = 'fixed no label')
            el = self.els.add_static('static', 'Static', 'static val')
            el = self.els.add_static('static-no-label', defaultval='static val no label')

and the view/controller code might look something like::

    class FormTest(HtmlTemplatePage):
        def prep(self):
            self.form = MyForm()

        def post(self):
            if self.form.is_cancel():
                self.assign('cancel', True)
            elif self.form.is_valid():
                self.assign('values', self.form.get_values())
            elif self.form.is_submitted():
                # form was submitted, but invalid
                self.form.assign_user_errors()
            self.default()

        def default(self):
            self.assign('form', self.form)

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Current Status
---------------

The code stays pretty stable, but the API may change, especially the rending.

The `blazeform tip <http://bitbucket.org/rsyring/blazeform/get/tip.zip#egg=blazeform-dev>`_
is installable via `easy_install` with ``easy_install blazeform==dev``
