from django.db import models
from django.conf import settings

class TranslationAllreadyRegistered(Exception):
    pass

class TranslationOptions(object):
    
    def __init__(self, options={}):
        self.language_field = options.get('language_field', 'language')
        self.translation_of_model = options.get('translation_of_model')
        self.translated_model = options.get('translated_model')
        self.translation_of_field = options.get('translation_of_field')
        self.translations_of_accessor = options.get('translations_of_accessor')
        self.translation_join_filter = options.get('translation_join_filter')
        
class TranslationPool(object):
    
    discovered = False
    translated_models_dict = {}
    translation_models_dict = {}
    
    def discover_translations(self):        
        if self.discovered:
            return
        for app in settings.INSTALLED_APPS:
            __import__(app, {}, {}, ['simple_translate'])
        self.discovered = True    

    def get_info(self, model):
        self.discover_translations()
        if model in self.translated_models_dict:
            return self.translated_models_dict[model]
        elif model in self.translation_models_dict:
            return self.translated_models_dict[ \
                self.translation_models_dict[model]
            ]
        
    def register_translation(self, translation_of_model, translated_model, \
        language_field='language'):
        
        assert issubclass(translation_of_model, models.Model) \
            and issubclass(translated_model, models.Model)
        
        if translation_of_model in self.translated_models_dict:
            raise TranslationAllreadyRegistered, \
                "[%s] a translation for this model is already registered" \
                    % translation_of_model.__name__
            
        options = {}    
        options['translated_model'] = translated_model
        
        opts = translation_of_model._meta
        for rel in opts.get_all_related_objects():
            if rel.model == translated_model:
                options['translation_of_field'] = rel.field.name
                options['translations_of_accessor'] = rel.get_accessor_name()

        options['translation_join_filter'] = translated_model.__name__.lower()          
        options['language_field'] = language_field     
        
        self.translated_models_dict[translation_of_model] = TranslationOptions(options)
        # keep track both ways
        self.translation_models_dict[translated_model] = translation_of_model

    def unregister_translation(self, translation_of_model):
        info = self.get_info(translation_of_model)
        del self.translation_models_dict[info.translated_model]
        del self.translated_models_dict[translation_of_model]
    
    def annotate_with_translations(self, list_or_instance):
        
        self.discover_translations()
        if not list_or_instance:
            return list_or_instance
        languages = [language_code for language_code, language_name in settings.LANGUAGES]
        
        model = list_or_instance.__class__ if isinstance(
            list_or_instance, models.Model
        ) else list_or_instance[0].__class__
        info = self.get_info(model)

        # Helper function that sorts translations according to settings.LANGUAGES
        def language_key(translation):
            l = getattr(translation, info.language_field)
            try:
                return languages.index(l)
            except ValueError:
                pass

        if isinstance(list_or_instance, models.Model):
            instance = list_or_instance
            if self.is_registered_translation(model):
                instance = getattr(list_or_instance, \
                    info.translation_of_field)
            
            translations = list(getattr(instance, \
            	info.translations_of_accessor).filter(**{'%s__in' % info.language_field: languages}))

            list_or_instance.translations = sorted(translations, key=language_key)
            
            return list_or_instance
        else:
            result_list = list_or_instance
            if not len(result_list):
                return result_list
                            
            id_list = [r.pk for r in result_list]
            pk_index_map = dict([(pk, index) for index, pk in enumerate(id_list)])
            
            translations = info.translated_model.objects.filter(**{
                info.translation_of_field + '__in': id_list,
                info.language_field + '__in': languages,
            })
            
            new_result_list = []
            for obj in translations:
                index = pk_index_map[getattr(obj, info.translation_of_field + '_id')]
                if not hasattr(result_list[index], 'translations'):
                    result_list[index].translations = []
                result_list[index].translations.append(obj)
            
            for result in result_list:
                result.translations = sorted(result.translations, key=language_key)
               
        return result_list
    
    def is_registered_translation(self, model):
        self.discover_translations()
        if model in self.translation_models_dict:
            return True
        return False
        
    def is_registered(self, model):
        self.discover_translations()
        if model in self.translated_models_dict:
            return True
        return False
            
translation_pool = TranslationPool()
