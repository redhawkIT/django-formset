import json
import pytest
import re
from pathlib import Path
from time import sleep

from django.core.signing import get_cookie_signer
from django.urls import path

from formset.views import FormView

from .forms.upload import UploadForm


class DemoFormView(FormView):
    template_name = 'testapp/native-form.html'
    form_class=UploadForm
    success_url = '/success'


urlpatterns = [path('upload', DemoFormView.as_view(), name='upload')]


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['upload'])
def test_upload_image(page, mocker):
    choose_file_button = page.query_selector('django-formset form button.dj-choose-file')
    assert choose_file_button is not None  # that button would open the file selector
    dropbox = page.query_selector('django-formset form ul.dj-dropbox')
    assert dropbox.inner_html() == '<li class="dj-empty-item">Drag file here</li>'
    page.set_input_files('#id_avatar', 'testapp/assets/python-django.png')
    file_picture = page.wait_for_selector('li.dj-file-picture')
    assert file_picture is not None
    img_src = file_picture.query_selector('img').get_attribute('src')
    match = re.match(r'^/((media/upload_temp/python-django\.[a-z0-9_]+?)_h128(.png))$', img_src)
    assert match is not None
    thumbnail_url = match.group(1)
    assert Path(thumbnail_url).exists()  # the thumbnail
    thumbnail_url = f'/{thumbnail_url}'
    download_url = match.group(2) + match.group(3)
    assert Path(download_url).exists()  # the uploaded file
    download_url = f'/{download_url}'
    file_caption = dropbox.query_selector('li.dj-file-caption')
    assert file_caption is not None
    figures = file_caption.query_selector_all('figure')
    assert len(figures) == 3
    assert figures[0].inner_html() == '<figcaption>Name:</figcaption><p>python-django.png</p>'
    assert figures[1].inner_html() == '<figcaption>Content-Type:</figcaption><p>image/png</p>'
    assert figures[2].inner_html() == '<figcaption>Size:</figcaption><p>16001</p>'
    button = file_caption.query_selector('a.dj-delete-file')
    assert button is not None
    assert button.inner_text() == 'Delete'
    button = file_caption.query_selector('a.dj-download-file')
    assert button is not None
    assert button.get_attribute('download') == 'python-django.png'
    assert button.get_attribute('href') == download_url
    spy = mocker.spy(DemoFormView, 'post')
    page.wait_for_selector('django-formset').evaluate('elem => elem.submit()')
    request = json.loads(spy.call_args.args[1].body)
    file = request['formset_data']['avatar'][0]
    signer = get_cookie_signer(salt='formset')
    upload_temp_name = signer.unsign(file['upload_temp_name'])
    assert (Path('media') / upload_temp_name).exists()
    assert file['name'] == 'python-django.png'
    assert file['download_url'] == download_url
    assert file['thumbnail_url'] == thumbnail_url
    assert file['content_type'] == 'image/png'
    assert file['size'] == 16001
    assert spy.spy_return.status_code == 200


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['upload'])
def test_upload_pdf(page):
    page.set_input_files('#id_avatar', 'testapp/assets/dummy.pdf')
    file_picture = page.wait_for_selector('django-formset form django-field-group li.dj-file-picture')
    assert file_picture is not None
    img_src = file_picture.query_selector('img').get_attribute('src')
    assert img_src == '/static/formset/icons/file-pdf.svg'


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['upload'])
def test_upload_broken_image(page):
    page.set_input_files('#id_avatar', 'testapp/assets/broken-image.jpg')
    file_picture = page.wait_for_selector('li.dj-file-picture')
    assert file_picture is not None
    img_src = file_picture.query_selector('img').get_attribute('src')
    assert img_src == '/static/formset/icons/file-picture.svg'


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['upload'])
def test_upload_required(page):
    field_group = page.query_selector('django-formset django-field-group')
    page.wait_for_selector('django-formset').evaluate('elem => elem.submit()')
    error_placeholder = field_group.wait_for_selector('.dj-errorlist .dj-placeholder')
    assert error_placeholder.inner_html() == "This field is required."


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['upload'])
def test_delete_uploaded_file(page):
    page.set_input_files('#id_avatar', 'testapp/assets/python-django.png')
    page.wait_for_selector('ul.dj-dropbox li.dj-file-picture')
    delete_button = page.wait_for_selector('ul.dj-dropbox li.dj-file-caption a.dj-delete-file')
    delete_button.click()
    empty_item = page.wait_for_selector('ul.dj-dropbox li.dj-empty-item')
    assert empty_item is not None


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['upload'])
def test_upload_progressbar(page):
    field_group = page.query_selector('django-formset django-field-group')
    client = page.context.new_cdp_session(page)
    client.send('Network.enable')
    network_conditions = {
        'offline': False,
        'downloadThroughput': 999999,
        'uploadThroughput': 9999,
        'latency': 20
    }
    client.send('Network.emulateNetworkConditions', network_conditions)
    test_image_path = Path('testapp/assets/python-django.png')
    assert test_image_path.exists()
    assert test_image_path.stat().st_size == 16001
    file_uploader = field_group.query_selector('#id_avatar')
    assert file_uploader is not None
    file_uploader.set_input_files([test_image_path])
    progress_bar = field_group.wait_for_selector('progress')
    assert progress_bar is not None
    progress_value = float(progress_bar.get_attribute('value'))
    assert progress_value >= 0.0 and progress_value <= 1.0
    sleep(0.2)
    progress_value = float(progress_bar.get_attribute('value'))
    assert progress_value > 0.0 and progress_value <= 1.0
    # thumbnailing image takes some time
    file_picture = field_group.wait_for_selector('li.dj-file-picture')
    assert file_picture is not None


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['upload'])
def test_upload_in_progress(page):
    field_group = page.wait_for_selector('django-formset django-field-group')
    client = page.context.new_cdp_session(page)
    client.send('Network.enable')
    network_conditions = {
        'offline': False,
        'downloadThroughput': 999999,
        'uploadThroughput': 512,
        'latency': 20
    }
    client.send('Network.emulateNetworkConditions', network_conditions)
    page.set_input_files('#id_avatar', 'testapp/assets/python-django.png')
    sleep(0.02)
    page.wait_for_selector('django-formset').evaluate('elem => elem.submit()')
    error_placeholder = field_group.wait_for_selector('.dj-errorlist .dj-placeholder')
    assert error_placeholder.inner_html() == "File upload still in progress."


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['upload'])
def test_interupt_upload(page):
    def handle_route(route):
        sleep(0.01)
        route.abort()

    field_group = page.query_selector('django-formset django-field-group')
    page.context.route('/upload', handle_route)
    page.set_input_files('#id_avatar', 'testapp/assets/python-django.png')
    sleep(0.02)
    error_placeholder = field_group.wait_for_selector('.dj-errorlist .dj-placeholder')
    assert error_placeholder.inner_html() == "File upload failed."
