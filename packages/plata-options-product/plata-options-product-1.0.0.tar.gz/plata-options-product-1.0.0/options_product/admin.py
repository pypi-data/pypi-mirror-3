from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

import plata
from . import models


class ProductPriceInline(admin.TabularInline):
    model = models.ProductPrice
    extra = 0

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 0


class ProductForm(forms.ModelForm):
    sku = forms.CharField(label=_('SKU'), max_length=100, required=False)
    create_variations = forms.BooleanField(label=_('Create all variations'), required=False)

    class Meta:
        model = models.Product

    def save(self, *args, **kwargs):
        instance = super(ProductForm, self).save(*args, **kwargs)
        instance._cleaned_data = self.cleaned_data
        return instance


class ProductVariationFormSet(BaseInlineFormSet):
    def clean(self):
        super(ProductVariationFormSet, self).clean()

        # This method ensures two things:
        # 1. No combination of options occurs twice
        # 2. SKUs are filled out and unique
        # 3. Active products have at least one active variation
        variations = set()
        skus = set()
        is_active_flags = []

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                if form.instance.pk and not form.instance.can_delete():
                    raise forms.ValidationError(
                        _('Cannot delete variation %s which has already been used in an order.') % form.instance)

            if (not form.instance.pk and not form.has_changed()) or \
                    (not form.is_valid()):
                # Skip forms which will not end up as instances or aren't valid yet
                continue

            options = form.cleaned_data.get('options')

            if options:
                s = tuple(sorted(o.id for o in options))

                if s in variations:
                    form._errors['options'] = form.error_class([
                        _('Combination of options already encountered.')])
                    continue

                variations.add(s)

            sku = form.cleaned_data.get('sku')
            if not sku or sku in skus:
                # Need to regenerate SKU
                parts = [self.instance.sku]
                parts.extend(o.value for o in options)
                sku = u'-'.join(parts)

                while sku in skus:
                    sku += u'-'

                form.instance.sku = sku
            skus.add(form.instance.sku)
            is_active_flags.append(form.instance.is_active)

        if self.instance.is_active and is_active_flags and not any(is_active_flags):
            raise forms.ValidationError(_('The product is active but does not have any active variations.'))


class ProductVariationForm(forms.ModelForm):
    sku = forms.CharField(label=_('SKU'), max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super(ProductVariationForm, self).__init__(*args, **kwargs)

        # :-(
        import inspect
        frame = inspect.currentframe()
        groups = None
        try:
            while frame.f_back:
                if 'form' in frame.f_locals.keys():
                    form = frame.f_locals['form']
                    try:
                        groups = form.cleaned_data.get('option_groups')
                        break
                    except AttributeError:
                        if form.instance and form.instance.pk:
                            groups = form.instance.option_groups.all()
                            break

                frame = frame.f_back
        except (AttributeError, KeyError):
            pass

        if groups is not None:
            self.fields['options'].queryset = models.Option.objects.filter(
                group__in=groups)

    def clean(self):
        options = self.cleaned_data.get('options', [])
        try:
            groups_on_product_objects = self.cleaned_data['product']._cleaned_data['option_groups']
        except AttributeError: # product form is not valid
            groups_on_product_objects = []
        groups_on_product = set(g.id for g in groups_on_product_objects)
        groups_on_variation = [o.group_id for o in options]
        options_errors = []

        if len(groups_on_variation) != len(set(groups_on_variation)):
            options_errors.append(_('Only one option per group allowed.'))
        if groups_on_product != set(groups_on_variation):
            if len(groups_on_product_objects):
                options_errors.append(_('Please select options from the following groups: %s') %\
                    u', '.join(unicode(g) for g in groups_on_product_objects))
            else:
                options_errors.append(
                    _('You need to select the following groups before this variation can be created: %s') %\
                    u', '.join(unicode(g) for g in models.OptionGroup.objects.filter(id__in=groups_on_variation)))

        if options_errors:
            self._errors['options'] = self.error_class(options_errors)

        self.instance._regenerate_cache(options=options)
        return self.cleaned_data


class ProductVariationInline(admin.TabularInline):
    model = models.ProductVariation
    form = ProductVariationForm
    formset = ProductVariationFormSet
    extra = 0
    readonly_fields = ('items_in_stock',)

class OptionInline(admin.TabularInline):
    model = models.Option


class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories', 'option_groups')
    form = ProductForm
    inlines = [ProductVariationInline, ProductPriceInline, ProductImageInline]
    list_display = ('is_active', 'is_featured', 'name', 'sku', 'ordering')
    list_display_links = ('name',)
    list_filter = ('is_active', 'is_featured', 'categories')
    prepopulated_fields = {'slug': ('name',), 'sku': ('name',)}
    search_fields = ('name', 'sku', 'description')

    def save_formset(self, request, form, formset, change):
        variations = isinstance(formset, ProductVariationFormSet)

        formset.save()

        if variations:
            if form.cleaned_data.get('create_variations'):
                form.instance.create_variations()
            elif form.instance.pk and\
                    not form.instance.option_groups.count() and\
                    not form.instance.variations.count():
                # No options selected, no variations yet: Create the single
                # variation which is needed
                form.instance.create_variations()


admin.site.register(models.Category,
    list_display=('is_active', 'is_internal', '__unicode__', 'ordering'),
    list_display_links=('__unicode__',),
    list_filter=('is_active', 'is_internal'),
    prepopulated_fields={'slug': ('name',)},
    search_fields=('name', 'description'),
    )

admin.site.register(models.OptionGroup,
    inlines=[OptionInline],
    list_display=('name',),
    )


if settings.OPTIONS_PRODUCT_FEINCMS:
    from feincms.admin.item_editor import ItemEditor, FEINCMS_CONTENT_FIELDSET

    class CMSProductAdmin(ProductAdmin, ItemEditor):
        fieldsets = [(None, {
            'fields': ('is_active', 'name', 'slug', 'sku', 'is_featured'),
            }),
            FEINCMS_CONTENT_FIELDSET,
            (_('Properties'), {
                'fields': ('ordering', 'description', 'producer', 'categories',
                    'option_groups', 'create_variations'),
            }),
            ]
        inlines = [ProductVariationInline, ProductPriceInline, ProductImageInline]

    admin.site.register(models.Product, CMSProductAdmin)
else:
    admin.site.register(models.Product, ProductAdmin)


class ReadonlyModelAdmin(admin.ModelAdmin):
    actions = None # no "delete selected objects" action
    def has_delete_permission(self, request, obj=None):
        return False

# All fields are read only; these models are only used for raw_id_fields support
admin.site.register(models.ProductPrice,
    admin_class=ReadonlyModelAdmin,
    list_display=('__unicode__', 'product', 'currency', '_unit_price', 'tax_included',
        'tax_class', 'is_active', 'valid_from', 'valid_until', 'is_sale'),
    list_filter=('is_active', 'is_sale', 'tax_included', 'tax_class', 'currency'),
    readonly_fields=('product', 'currency', '_unit_price', 'tax_included', 'tax_class',
        'is_active', 'valid_from', 'valid_until', 'is_sale'),
    search_fields=('product__name', 'product__description', '_unit_price'),
    can_delete=False,
    )

admin.site.register(models.ProductVariation,
    admin_class=ReadonlyModelAdmin,
    list_display=('__unicode__', 'is_active', 'sku', 'items_in_stock', 'ordering'),
    list_filter=('is_active',),
    readonly_fields=('product', 'is_active', 'sku', 'items_in_stock', 'options', 'ordering'),
    search_fields=('sku', 'product__name', 'product__description'),
    )
