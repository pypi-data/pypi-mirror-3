from django.db import models

from treebeard.mp_tree import MP_Node
from treebeard.al_tree import AL_Node
from treebeard.ns_tree import NS_Node

class DocumentCategoryMixin(models.Model):
    collection_instance = models.CharField(max_length=128, db_index=True)
    document_id = models.CharField(max_length=128, db_index=True)
    
    created = models.DateTimeField(default=datetime.now, editable=False)
    order = models.IntegerField(default=0)

    #visibility flags    
    staff_only = models.BooleanField(default=False)
    authenticated_users_only = models.BooleanField(detault=False)
    listed = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        abstract = True
    
    def get_document(self):
        raise NotImplementedError

class MP_DoucmentCategory(MP_Node, DocumentCategoryMixin):
    node_order_by=['order']
    
    class Meta:
        ordering = ['path'] #this value shouldn't be changed

class AL_DoucmentCategory(AL_Node, DocumentCategoryMixin):
    node_order_by=['order']
    
    parent = models.ForeignKey('self',
                               related_name='children_set',
                               null=True,
                               db_index=True)

class NS_DoucmentCategory(NS_Node, DocumentCategoryMixin):
    node_order_by=['order']
    
    class Meta:
        ordering = ['tree_id', 'lft'] #this value shouldn't be changed
