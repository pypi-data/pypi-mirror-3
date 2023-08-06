from dockitcms.viewpoints.forms import TemplateFormMixin
from dockitcms.viewpoints.common import CanonicalMixin, TemplateMixin

from common import CollectionMixin, PointListView, PointDetailView, LIST_CONTEXT_DESCRIPTION, DETAIL_CONTEXT_DESCRIPTION

from dockitcms.models import ViewPoint

from dockit import schema
from dockit.forms import DocumentForm

from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django import forms

class BaseCollectionViewPoint(ViewPoint, CollectionMixin, TemplateMixin):
    view_class = None
    
    class Meta:
        proxy = True
    
    @classmethod
    def get_admin_form_class(cls):
        return BaseCollectionViewPointForm
    
    def register_view_point(self):
        index = self.get_base_index()
        index.commit()

class CollectionListViewPoint(BaseCollectionViewPoint):
    paginate_by = schema.IntegerField(blank=True, null=True)
    #TODO order by
    
    view_class = PointListView
    
    def get_urls(self):
        params = self.to_primitive(self)
        document = self.get_document()
        index = self.get_base_index()
        urlpatterns = patterns('',
            url(r'^$', 
                self.view_class.as_view(document=document,
                                      queryset=index,
                                      view_point=self,
                                      configuration=params,
                                      paginate_by=self.paginate_by),
                name='index',
            ),
        )
        return urlpatterns
    
    class Meta:
        typed_key = 'dockitcms.collectionlistview'
    
    @classmethod
    def get_admin_form_class(cls):
        return CollectionListViewPointForm

class CollectionDetailViewPoint(BaseCollectionViewPoint, CanonicalMixin):
    slug_field = schema.SlugField(blank=True)
    
    view_class = PointDetailView
    
    def get_document(self):
        document = super(CollectionDetailViewPoint, self).get_document()
        view_point = self
        
        def get_absolute_url_for_instance(instance):
            if view_point.slug_field:
                return view_point.reverse('detail', instance[view_point.slug_field])
            return view_point.reverse('detail', instance.pk)
        
        if self.canonical:
            document.get_absolute_url = get_absolute_url_for_instance
        
        return document
    
    def get_base_index(self):
        index = super(CollectionDetailViewPoint, self).get_base_index()
        if self.slug_field:
            index = index.index(self.slug_field)
        return index
    
    def get_urls(self):
        params = self.to_primitive(self)
        document = self.get_document()
        index = self.get_base_index()
        if self.slug_field:
            return patterns('',
                url(r'^(?P<slug>.+)/$',
                    self.view_class.as_view(document=document,
                                          queryset=index,
                                          view_point=self,
                                          configuration=params,
                                          slug_field=self.slug_field,),
                    name='index',
                ),
            )
        else:
            return patterns('',
                url(r'^(?P<pk>.+)/$',
                    self.view_class.as_view(document=document,
                                          queryset=index,
                                          view_point=self,
                                          configuration=params,),
                    name='index',
                ),
            )
    
    class Meta:
        typed_key = 'dockitcms.collectiondetailview'
    
    @classmethod
    def get_admin_form_class(cls):
        return CollectionDetailViewPointForm

class BaseCollectionViewPointForm(TemplateFormMixin, DocumentForm):
    class Meta:
        document = BaseCollectionViewPoint

class CollectionListViewPointForm(BaseCollectionViewPointForm):
    template_name = forms.CharField(initial='dockitcms/list.html', required=False)
    content = forms.CharField(help_text=LIST_CONTEXT_DESCRIPTION, required=False, widget=forms.Textarea)

class CollectionDetailViewPointForm(BaseCollectionViewPointForm):
    template_name = forms.CharField(initial='dockitcms/detail.html', required=False)
    content = forms.CharField(help_text=DETAIL_CONTEXT_DESCRIPTION, required=False, widget=forms.Textarea)

