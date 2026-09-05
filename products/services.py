from django.db import transaction


def create_product_with_variant(form_image, form, formset):
    if not form.is_valid():
        return None, 'InvalidForm'
    if not formset.is_valid():
        return None, 'InvalidFormset'

    if not form_image.is_valid():
        return None, 'InvalidFormImage'

    with transaction.atomic():
        product = form.save()

        formset.instance = product
        form_image.instance = product

        variants = formset.save(commit=False)
        images = form_image.save(commit=False)

        for variant in variants:
            variant.product = product
            variant.save()

        for image in images:
            image.product = product
            image.save()

    return product, 'Created'


def update_product_with_variant(form_image, form, formset):
    if not form.is_valid():
        return None, 'InvalidForm'
    if not formset.is_valid():
        return None, 'InvalidFormset'
    if not form_image.is_valid():
        return None, 'InvalidFormImage'

    with transaction.atomic():
        product = form.save()

        formset.instance = product
        formset.save()

        form_image.instance = product
        form_image.save()

    return product, 'Updated'

