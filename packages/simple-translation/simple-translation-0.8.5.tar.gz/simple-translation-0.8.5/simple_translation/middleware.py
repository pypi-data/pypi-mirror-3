from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.utils import translation

from simple_translation.translation_pool import translation_pool

def filter_queryset_language(request, queryset):
    language = getattr(request, 'LANGUAGE_CODE')
    model = queryset.model
    filter_expr = None
    if translation_pool.is_registered(model):
        info = translation_pool.get_info(model)
        filter_expr = '%s__%s' % (info.translation_join_filter, info.language_field)
    if translation_pool.is_registered_translation(model):
        info = translation_pool.get_info(model)
        filter_expr = '%s' % info.language_field
    if filter_expr:
        queryset = queryset.filter( \
            **{filter_expr: language}).distinct()
    return queryset
    
class MultilingualGenericsMiddleware(LocaleMiddleware):
    
    language_fallback_middlewares = ['django.middleware.locale.LocaleMiddleware']
    
    def has_language_fallback_middlewares(self):
        has_fallback = False
        for middleware in self.language_fallback_middlewares: 
            if middleware in settings.MIDDLEWARE_CLASSES:
                has_fallback = True
        return has_fallback

    def process_view(self, request, view_func, view_args, view_kwargs):
        language = None
        if 'language_code' in view_kwargs:
            # get language and set tralslation
            language = view_kwargs.pop('language_code')
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()

        if 'queryset' in view_kwargs:
            view_kwargs['queryset'] = filter_queryset_language(request, view_kwargs['queryset'])  

    def process_response(self, request, response):
        if not self.has_language_fallback_middlewares():
            return super(MultilingualGenericsMiddleware, self).process_response(request, response)
        return response