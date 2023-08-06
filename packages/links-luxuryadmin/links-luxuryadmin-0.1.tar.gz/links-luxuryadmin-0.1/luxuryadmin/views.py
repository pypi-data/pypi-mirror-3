from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.utils import simplejson

from sorl.thumbnail import get_thumbnail

from .forms import LoginForm, ProductForm, ProductTableRow
from .utils import random_filename, slugify

from collection.models import Product, Photo, Category


@user_passes_test(lambda u: u.is_staff)
def collection(request):
    table_rows = []
    for category in Category.objects.all():
        products = category.products
        if products.count() < 1:
            continue
        table_rows.append(dict(
            category=category,
            products=[dict(
                    row=ProductTableRow(instance=product),
                    form=ProductForm(instance=product)
                ) for product in products.all()]
        ))

    return TemplateResponse(request, 'luxuryadmin/collection.html', dict(
        form_new_product=ProductForm,
        table_rows=table_rows
    ))


@user_passes_test(lambda u: u.is_staff)
def xhr_upload_photo(request):
    """Upload photos from form, return filenames and urls and thumbnails."""
    def handle_uploaded_image(orig_filename, f):
        path, _, filename = random_filename(settings.MEDIA_PATH['product'],
            ext=orig_filename.split('.')[-1])
        destination = open(path, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        return {
            'path': path,
            'filename': filename
        }

    if request.method != 'POST':
        return HttpResponse(simplejson.dumps({
            'success': False,
            'errors': ['POST, please.']
        }))

    images = [handle_uploaded_image(name, image) for name, image in \
        request.FILES.items()]

    for image in images:
        image['thumb'] = get_thumbnail(image['filename'], '64x48').url
        image['url'] = settings.MEDIA_URL + image['filename']
        del image['path']

    response = {
        'images': images
    }
    return HttpResponse(simplejson.dumps(response))


@user_passes_test(lambda u: u.is_staff)
def xhr_update_photos(request):
    try:
        product = Product.objects.get(pk=request.POST['pk'])
    except Product.DoesNotExist:
        raise Http404

    i = 1
    images = simplejson.loads(request.POST['images'])
    existing = product.photos.all()
    new = []
    for image in images:
        photo, created = Photo.objects.get_or_create(image=image['filename'],
            product=product, defaults=dict(
                sort_index=99
            ))
        if image['selected']:
            photo.sort_index = 0
        else:
            photo.sort_index = i
            i += 1

        photo.save()
        new.append(photo)

    for e in existing:
        if e not in new:
            e.delete()

    response = {}
    return HttpResponse(simplejson.dumps(response))


@user_passes_test(lambda u: u.is_staff)
def xhr_save_product(request, pk=None, type=None):
    if type == 'tablerow':
        cls = ProductTableRow
    else:
        cls = ProductForm
    if pk:
        try:
            p = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404
        f = cls(request.POST, instance=p)

    else:
        f = cls(request.POST)

    if f.is_valid():
        product = f.save(commit=False)
        if not pk:
            product.slug = slugify(request.POST['name'])
            product.num_views = 0
            product.in_date = datetime.now()

        product.live = True
        product.save()

        return HttpResponse(simplejson.dumps({
            'success': True,
            'pk': product.pk
        }))

    return HttpResponse(simplejson.dumps({
        'success': False,
        'errors': f.errors
    }))


def xhr_log_in(request):
    form = LoginForm(request.POST)
    success = False
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'],
            password=form.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                success = True

    return HttpResponse(simplejson.dumps({
        'success': success
    }))


def log_out(request):
    logout(request)
    return redirect('/')
