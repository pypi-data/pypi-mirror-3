# -*- coding: utf-8 -*-
import os
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.db.models import Q, BooleanField, NullBooleanField
from django.db.models.fields import FieldDoesNotExist
from django.views.generic import (TemplateView, ListView, 
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)

# -----------------------
# INTRANET CONTEXT MIXINS
# -----------------------

class IntranetModelContextMixin(object):

    url_list = None
    url_detail = None
    url_add = None
    url_edit = None
    url_delete = None
    url_cancel = None

    def get_module_name(self):
        if self.model:
            return self.model._meta.module_name
        return ''

    def get_app_label(self):
        if self.model:
            return self.model._meta.app_label
        return ''

    def get_url(self, suffix):
        url = getattr(self, 'url_%s' % suffix, None)
        if url:
            return url
        else:
            return u'%s-%s' % (self.get_module_name(), suffix)

    def get_cancel_url(self):
        if self.url_cancel:
            return self.get_url(self.url_cancel)
        obj = getattr(self, 'object', None)
        if obj:
            return self.get_url('detail')
        return self.get_url('list')

    def get_urls(self):
        urls = {}
        for suffix in ['list', 'detail', 'add', 'edit', 'create', 'delete']:
            urls[suffix] = self.get_url(suffix)
        urls['cancel'] = self.get_cancel_url()
        return urls

    def get_success_url(self):
        obj = getattr(self, 'object', None)
        if obj:
            return reverse(self.get_url('detail'), args=[self.object.pk])
        return None

    def get_template_names(self):
        """
        Get the templates list to use for rendering.

        We first return the `template_name` attribute of the view,
        then the specific template of model (e.g. 'intranet/entrepreneur/model_list.html'),
        finaly, the generic template ('intranet/model_list.html').
        """
        app_label = self.model._meta.app_label
        module_name = self.model._meta.module_name
        base_template_name = u'model%s.html' % self.template_name_suffix

        template_list = []
        # Specific `template_name` of the view
        if self.template_name:
            template_list.append(self.template_name)
        # Specific template for app
        template_list.append(os.path.join(app_label, module_name, base_template_name))
        # Default template
        template_list.append(os.path.join('intranet', base_template_name))
        return template_list

    def get_context_data(self, **kwargs):
        context = super(IntranetModelContextMixin, self).get_context_data(**kwargs)
        # Add global template data
        model = getattr(self, 'model', None)
        if model:
            context['module_name'] = self.get_module_name()
            context['app_label'] = self.get_app_label()
            context['verbose_name'] = model._meta.verbose_name
            context['verbose_name_plural'] = model._meta.verbose_name_plural
        context['urls'] = self.get_urls()
        return context


# -----------------------
# INTRANET PERMS MIXINS
# -----------------------

class IntranetPermsMixin(object):
    perms = None
    prefix_perms = None
    perms_object = None
    perms_object_allowed = True

    def dispatch(self, request, *args, **kwargs):
        """
        Overload the super method and add checking rights access.

        If user in request has permissions required, normal response is returned.
        Else, the normal response is avorted and a response with a single message
        is returned.
        """
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        # Check rights user
        if self.has_perms():
            return handler(request, *args, **kwargs)
        else:
            return HttpResponse('Sorry, access forbidden !')
       

    def get_user(self):
        return getattr(self.request, 'user', None)
        
    def get_perms(self):
        perms = []
        if self.perms:
            perms += self.perms
        if self.prefix_perms:
            if hasattr(self, 'get_app_label') and\
                    hasattr(self, 'get_module_name'):
                app_label = self.get_app_label()
                module_name = self.get_module_name()
                perms += ['%s.%s_%s' % (app_label, prefix, module_name)
                          for prefix in self.prefix_perms]
        return tuple(perms)

    def get_perms_object(self):
        perms_object = []
        if self.perms_object_allowed:
            if self.perms_object:
                perms_object += self.perms_object
            if self.prefix_perms:
                if hasattr(self, 'get_module_name'):
                    module_name = self.get_module_name()
                    perms_object += ['%s_%s' % (prefix, module_name)
                                     for prefix in self.prefix_perms]
        return tuple(perms_object)

    def get_object_for_perms(self):
        return self.get_object()

    def has_perms(self, *args, **kwargs):
        user = self.get_user()
        is_authorized = True
        perms = self.get_perms()
        perms_object = self.get_perms_object()
        # Perms required and not user
        # => Access denied
        if (perms or perms_object) and not user:
            return False
        # Global perms.
        if perms:
            for perm in perms:
                if not user.has_perm(perm):
                    is_authorized = False
                    break
        # Specific object perms.
        # Checked only if user is currently not allowed with global perms.
        if perms_object and (not is_authorized):
            obj = self.get_object_for_perms()
            for perm in perms_object:
                if user.has_perm(perm, obj):
                    is_authorized = True
                    break
        return is_authorized


# -------------------
# INTRANET VIEWS
# -------------------

class IntranetBaseView(IntranetPermsMixin, TemplateView):
    pass

class IntranetListView(IntranetModelContextMixin, ListView):
    list_display = None
    list_display_links = None
    search_fields = None
    list_filter = []

    search_url = ''
    ordering_url = ''
    filters_url = ''

    default_ordering_index = None
    default_ordering_asc = True


    def _append_to_url(self, url, param, value):
        if url:
            url += '&'
        url += u'%s=%s' % (param, value)

    def get_queryset(self):
        queryset = super(IntranetListView, self).get_queryset()
        if self.request.method == 'GET':
            q = self.request.GET.get('q', None)
            if q and self.search_fields is not None:
                self.search_url = 'q=%s' % q
                global_filter = Q()
                for field in self.search_fields:
                    searching_filter = u'%s__icontains' % field
                    global_filter |= Q(**{searching_filter:q})
                queryset = queryset.filter(global_filter)
        # LIST FILTERS
        self._apply_filters_params()
        if self.active_filters:
            query_filters = Q()
            for item, value in self.active_filters.items():
                filter_name = '%s__exact' % item
                query_filters &= Q(**{filter_name:value})
            queryset = queryset.filter(query_filters)
        # ORDERING FIELD
        self._apply_ordering_params()
        if self.ordering_field:
            # Model Field
            try:
                field = self.model._meta.get_field(self.ordering_field)
            except FieldDoesNotExist:
                field = None
            if field:
                ordering_str = self.ordering_field
            elif hasattr(self.model, self.ordering_field):
                attr = getattr(self.model, self.ordering_field)
                ordering_str = getattr(attr, 'admin_order_field', '')
            if ordering_str:
                if not self.ordering_asc:
                    ordering_str = '-%s' % ordering_str
                queryset = queryset.order_by(ordering_str)
            else:
                self.ordering_field = None

        if not self.ordering_field:
            default_ordering = self.model._meta.ordering
            print "DEFAULT ORDERING... :", default_ordering
            if default_ordering:
                queryset = queryset.order_by(*default_ordering)
        return queryset

    def _apply_ordering_params(self):
        self.ordering_field = None
        self.ordering_asc = True
        self.ordering_index = None
        if self.request.method != 'GET':
            return
        # Check if ordering asked
        ordering_params = self.request.GET.get('o')
        if ordering_params:
            self.ordering_url = 'o=%s' % ordering_params
            # Ordering Way
            if ordering_params.startswith('-'):
                self.ordering_asc = False
                ordering_params = ordering_params[1:]
            # Ordering Field
            try:
                self.ordering_index = int(ordering_params)-1
                self.ordering_field = self.list_display[self.ordering_index]
            except (ValueError, IndexError):
                # Disable ordering
                pass
        #elif self.list_display and self.default_ordering_index:
        
        #else:
        #    try:
        #        #print "-----------------------", self.default_ordering_index
        #        #print "-----------------------", self.list_display
        #        self.ordering_field = self.list_display[self.default_ordering_index]
        #        self.ordering_index = self.default_ordering_index
        #        self.ordering_asc = self.default_ordering_asc
        #    except (IndexError, TypeError):
        #        print "EXCEPTION...."
        #        self.ordering_field = None
        #        self.ordering_index = None
        
        # elif self.list_display:
        #    # By Default, we order by the first field displayed
        #    self.ordering_index = 0
        #    self.ordering_field = self.list_display[self.ordering_index]

    def _apply_filters_params(self):
        self.active_filters = {}
        if self.request.method != 'GET' and self.list_filter:
            return
        for field in self.list_filter:
            value = self.request.GET.get(field, '')
            if value != '':
                self.active_filters[field] = value
        self.filters_url = '&'.join(['%s=%s' % (key, value)
                                     for key, value in self.active_filters.items()])

    def get_context_list_display(self):
        # Current Url with search and filters params
        params_url_items = []
        if self.search_url:
            params_url_items.append(self.search_url)
        if self.filters_url:
            params_url_items.append(self.filters_url)
        params_url = '&'.join(params_url_items)
        if params_url:
            current_url = '?%s&' % params_url
        else:
            current_url = '?'
        # --
        # Check if fields are valid
        context_list_display = []
        model_fields_list = self.model._meta.get_all_field_names()
        if self.list_display is not None:
            for field in self.list_display:
                item = {}
                if field in model_fields_list:
                    model_field = self.model._meta.get_field(field)
                    item['verbose_name'] = model_field.verbose_name
                    # Boolean 'on'/'off' displaying
                    if isinstance(model_field, BooleanField) or\
                            isinstance(model_field, NullBooleanField):
                        item['boolean'] = True
                elif hasattr(self.model, field):
                    attr = getattr(self.model, field)
                    item['callable'] = True
                    if hasattr(attr, 'short_description'):
                        item['verbose_name'] = getattr(attr, 'short_description')
                    else:
                        item['verbose_name'] = attr.__name__
                    # Boolean 'on'/'off' displaying
                    item['boolean'] = getattr(attr, 'boolean', False)
                if item:
                    item['field'] = field
                    if self.ordering_field == field:
                        item['ordering'] = True
                        item['ordering_asc'] = self.ordering_asc
                        if self.ordering_asc:
                            item['ordering_url'] = '%so=-%s' % (current_url, self.ordering_index+1)
                        else:
                            item['ordering_url'] = '%so=%s' % (current_url, self.ordering_index+1)
                    else:
                        item['ordering_url'] = '%so=%s' % (current_url, self.list_display.index(field)+1)
                    context_list_display.append(item)
                else:
                    raise ImproperlyConfigured("%s : Model `%s` hasn't field named `%s`." % (
                            self.__class__.__name__, self.model.__name__, field))
        return context_list_display

    def get_context_list_filter(self):
        context_list_filter = []
        # Current url with search and ordering params
        params_url = []
        if self.search_url:
            params_url.append(self.search_url)
        if self.ordering_url:
            params_url.append(self.ordering_url)
        # --
        for field in self.list_filter:
            infos = {}
            # Verbose Name
            model_fields_list = self.model._meta.get_all_field_names()
            if field in model_fields_list:
                verbose_name = self.model._meta.get_field(field).verbose_name
            elif hasattr(self.model, field):
                attr = getattr(self.model, field)
                if hasattr(attr, 'short_description'):
                    verbose_name = getattr(attr, 'short_description')
                else:
                    verbose_name = attr.__name__
            infos['verbose_name'] = verbose_name
            # URLs
            params_filters_url = '&'.join(['%s=%s' % (key, value)
                                          for key, value in self.active_filters.items()
                                          if key != field])
            if params_filters_url:
                global_params_url = params_url + [params_filters_url]
            else:
                global_params_url = list(params_url)
            infos['url'] = {'none': '?%s' % '&'.join(global_params_url),
                            'yes': '?%s=1' % '&'.join(global_params_url+[field]),
                            'no': '?%s=0' % '&'.join(global_params_url+[field])}
            # Current Value
            if field in self.active_filters.keys():
                infos['value'] = self.active_filters[field]
            context_list_filter.append(infos)
        return context_list_filter
        
    def get_context_data(self, **kwargs):
        context = super(IntranetListView, self).get_context_data(**kwargs)
        context['list_display'] = self.get_context_list_display()
        context['list_display_links'] = self.list_display_links
        context['search_fields'] = self.search_fields
        context['list_filter'] = self.get_context_list_filter()
        context['active_filters'] = [(key, value) for key, value in self.active_filters.items()]
        return context

class IntranetDetailView(IntranetPermsMixin, IntranetModelContextMixin, DetailView):
    def get_list_queryset(self):
        STEP = 5
        LIST_SIZE = 2*STEP+1
        current_object = self.get_object()
        print 'oooooooooooo', self.model._meta.ordering
        query_set = self.model.objects.order_by(*self.model._meta.ordering)
        index = list(query_set).index(current_object)
        
        # Index too close to start
        if index < STEP:
            start_ind = 0
            end_ind = LIST_SIZE # We don't care if it's too big.
        # Index too close to end
        elif index+STEP >= len(query_set):
            end_ind = len(query_set)
            start_ind = end_ind>=LIST_SIZE and end_ind-LIST_SIZE or 0
        else:
            start_ind = index-STEP
            end_ind = start_ind+LIST_SIZE
        
        return query_set[start_ind:end_ind]

    def get_context_data(self, **kwargs):
        context = super(IntranetDetailView, self).get_context_data(**kwargs)
        context['object_list'] = self.get_list_queryset()
        return context


class IntranetCreateView(IntranetPermsMixin, IntranetModelContextMixin, CreateView):
    url_cancel = 'list'
    perms_object_allowed = False
    prefix_perms = ('add',)


class IntranetUpdateView(IntranetPermsMixin, IntranetModelContextMixin, UpdateView):
    url_cancel = 'detail'
    prefix_perms = ('change',)


class IntranetSectionUpdateView(IntranetUpdateView):
    section = None
    sections_filter = None

    def dispatch(self, *args, **kwargs):
        # Save the section model
        self.section = kwargs.get('section', None)
        # If filter sections, we check if
        # this section is allowed.
        if self.section is not None and\
                self.sections_filter is not None:
            if self.section not in self.sections_filter:
                raise Http404
        # Default Process
        return super(IntranetSectionUpdateView, self).dispatch(*args, **kwargs)

    def get_form_class(self):
        if self.section is not None:
            form_class_name = u'%sSection%sForm' % ( self.model.__name__, self.section.capitalize())
            module_name = '%s.forms' % self.model.__module__.rsplit('.', 1)[0]
            try:
                module = __import__(module_name, fromlist=[form_class_name])
                form_class = getattr(module, form_class_name, None)
                if form_class:
                    return form_class
            except ImportError:
                pass
        # Default Case
        return super(IntranetSectionUpdateView, self).get_form_class()

    def get_context_data(self, **kwargs):
        context = super(IntranetSectionUpdateView, self).get_context_data(**kwargs)
        context['section'] = self.section
        return context

class IntranetDeleteView(IntranetPermsMixin, IntranetModelContextMixin, DeleteView):
    url_cancel = 'detail'
    prefix_perms = ('delete',)

    def get_success_url(self):
        return reverse(self.get_url('list'))
