from json import dump

from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.fields.related import ForeignKey
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponse
from django.views.generic import (ListView, DetailView, CreateView, UpdateView,
    DeleteView)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator


class AllInOneViewBase(type):

    def __new__(cls, *args, **kwargs):

        cls = type.__new__(cls, *args, **kwargs)

        cls.pk_name = '%s_pk' % (cls.context_object_name or
            cls.__name__.lower())

        cls.children = map(
            lambda (child_name, child_class): (child_name, child_class()),
            cls.children)

        class AIOBaseMixin(object):

            parent = None

            def dispatch(self, request, *args, **kwargs):

                if cls.pk_name in kwargs:
                    kwargs['pk'] = kwargs[cls.pk_name]

                return super(AIOBaseMixin, self).dispatch(request, *args,
                    **kwargs)

            def render_to_response(self, context):
                if 'as_child' in self.kwargs and self.kwargs['as_child']:
                    response = context
                elif self.request.is_ajax():
                    response = HttpResponse(content_type='application/json')
                    dump(context, response)
                else:
                    response = super(AIOBaseMixin,
                        self).render_to_response(context)
                return response

            def get_queryset(self):
                queryset = cls.get_queryset(self.request, **self.kwargs)

                if not isinstance(queryset, QuerySet):
                    queryset = super(AIOBaseMixin, self).get_queryset()

                return queryset

            def get_context_data(self, **kwargs):
                context = super(AIOBaseMixin, self).get_context_data(**kwargs)

                if self.parent:
                    context.update({self.parent.get_context_object_name():
                        self.parent.get_object(
                            self.kwargs[self.parent.get_pk_name()])})

                return context

        class OwnerObjectMixin(object):
            def get_owner_object(self, queryset=None):
                object = SingleObjectMixin.get_object(self, queryset=queryset)
                if getattr(object, cls.owner_field_name) == self.request.user:
                    return object
                else:
                    raise Http404

        class AIOListView(AIOBaseMixin, ListView):
            if cls.create_form_in_list:
                def get_context_data(self, **kwargs):
                    context = super(AIOListView, self).get_context_data(
                        **kwargs)
                    create_view = cls().as_create_view()
                    kwargs = {}
                    kwargs.update(self.kwargs)
                    parent_context = {}
                    parent_context.update(kwargs.pop('parent_context', {}))
                    parent_context.update(context)
                    kwargs.update({'as_child': True})
                    create_view_context = create_view(self.request,
                        parent_context=parent_context, **kwargs)
                    context.update(create_view_context)
                    return context

        class AIODetailView(AIOBaseMixin, DetailView):
            def get_context_data(self, **kwargs):
                context = super(AIODetailView, self).get_context_data(**kwargs)
                children_context = {}
                for _child_name, child in cls.children:
                    child_view = child.as_list_view()
                    children_context.update(child_view(self.request,
                        as_child=True, parent_context=context, **self.kwargs))
                context.update(children_context)
                return context

        class AIOCreateView(AIOBaseMixin, CreateView):
            def form_valid(self, form):
                self.object = form.save(commit=False)
                if cls.require_owner_to_update:
                    setattr(self.object, cls.owner_field_name,
                        self.request.user)
                if self.parent:
                    setattr(self.object, self.parent.get_fk_name(self.model),
                        self.parent.get_object(
                            self.kwargs[self.parent.get_pk_name()]))
                self.object.save()
                return FormMixin.form_valid(self, form)
            if cls.require_login_to_create:
                @method_decorator(login_required)
                def dispatch(self, request, *args, **kwargs):
                    return super(AIOCreateView, self).dispatch(request, *args,
                        **kwargs)

        class AIOUpdateView(AIOBaseMixin, OwnerObjectMixin, UpdateView):
            if cls.require_owner_to_update:
                get_object = OwnerObjectMixin.get_owner_object
            if cls.require_login_to_create:
                @method_decorator(login_required)
                def dispatch(self, request, *args, **kwargs):
                    return super(AIOUpdateView, self).dispatch(request, *args,
                        **kwargs)

        class AIODeleteView(AIOBaseMixin, OwnerObjectMixin, DeleteView):
            def get_success_url(self):
                return reverse('%s-list' % cls.context_object_name)
            if cls.require_owner_to_update:
                get_object = OwnerObjectMixin.get_owner_object
            if cls.require_login_to_create:
                @method_decorator(login_required)
                def dispatch(self, request, *args, **kwargs):
                    return super(AIODeleteView, self).dispatch(request, *args,
                        **kwargs)

        cls.ListView = AIOListView
        cls.DetailView = AIODetailView
        cls.CreateView = AIOCreateView
        cls.UpdateView = AIOUpdateView
        cls.DeleteView = AIODeleteView

        return cls


class AllInOneView(object):
    __metaclass__ = AllInOneViewBase

    paginate_by = None
    list_template_name = None
    detail_template_name = None
    form_template_name = None
    delete_template_name = None
    context_object_name = None
    model = None
    form_class = None
    require_login_to_create = True
    require_owner_to_update = True
    owner_field_name = 'owner'
    children = ()
    create_form_in_list = False

    def __init__(self, **kwargs):
        super(AllInOneView, self).__init__()
        self.__dict__.update(kwargs)

        if not self.model:
            raise Exception('Need to provide model class.')

    @classmethod
    def get_queryset(cls, request, **kwargs):
        return None

    def as_list_view(self, **kwargs):
        return self.ListView.as_view(
            template_name=self.list_template_name,
            model=self.model,
            context_object_name='%s_list' % self.context_object_name,
            paginate_by=self.paginate_by,
            **kwargs)

    def as_detail_view(self, **kwargs):
        return self.DetailView.as_view(
            template_name=self.detail_template_name,
            model=self.model,
            context_object_name=self.context_object_name,
            **kwargs)

    def as_create_view(self, **kwargs):
        return self.CreateView.as_view(
            template_name=self.form_template_name,
            model=self.model,
            context_object_name=self.context_object_name,
            form_class=self.form_class,
            **kwargs)

    def as_update_view(self, **kwargs):
        return self.UpdateView.as_view(
            template_name=self.form_template_name,
            model=self.model,
            context_object_name=self.context_object_name,
            form_class=self.form_class,
            **kwargs)

    def as_delete_view(self, **kwargs):
        return self.DeleteView.as_view(
            template_name=self.delete_template_name,
            model=self.model,
            **kwargs)

    def get_urlpatterns(self, url_prefix, parent=None):
        object_prefix = r'%s(?P<%s>\d+)/' % (url_prefix, self.pk_name)
        urlpatterns = patterns('',
            url(r'^%s$' % url_prefix,
                self.as_list_view(parent=parent),
                name='%s-list' % self.context_object_name),
            url(r'^%s$' % object_prefix,
                self.as_detail_view(parent=parent),
                name=self.context_object_name),
            url(r'^%sadd/$' % url_prefix,
                self.as_create_view(parent=parent),
                name='%s-add' % self.context_object_name),
            url(r'^%sedit/$' % object_prefix,
                self.as_update_view(parent=parent),
                name='%s-edit' % self.context_object_name),
            url(r'^%sdelete/$' % object_prefix,
                self.as_delete_view(parent=parent),
                name='%s-delete' % self.context_object_name))
        for child_name, child in self.children:
            urlpatterns += child.get_urlpatterns(
                object_prefix + '%s/' % child_name,
                parent=ParentAIOView(self.__class__))
        return urlpatterns


class ParentAIOView(object):

    def __init__(self, parent_class=None):

        if issubclass(parent_class, AllInOneView):
            self.parent_class = parent_class
        else:
            raise Exception('Parent class must be subclass of AllInOneView.')

    def get_pk_name(self):
        return self.parent_class.pk_name

    def get_fk_name(self, model):
        for field in model._meta.fields:
            if (isinstance(field, ForeignKey) and
              field.related.parent_model == self.parent_class.model):
                return field.name

    def get_context_object_name(self):
        return self.parent_class.context_object_name

    def get_object(self, pk):
        if not hasattr(self, 'object'):
            self.object = self.parent_class.model.objects.get(pk=pk)
        return self.object
