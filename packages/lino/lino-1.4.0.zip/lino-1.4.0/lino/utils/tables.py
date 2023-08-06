# -*- coding: UTF-8 -*-
## Copyright 2009-2012 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

u"""
>>> DATA = [ 
... ["Belgium", "Eupen", 17000] ,
... ["Belgium", u"Liège", 400000] ,
... ["Belgium", "Raeren", 5000] ,
... ["Estonia", "Tallinn", 400000] ,
... ["Estonia", "Vigala", 1500] ,
... ]


>>> class CitiesAndInhabitants(VirtualTable):
...     column_names = "country city population"
...     @classmethod
...     def get_data_rows(self,ar):
...         return DATA
...
...     @column(label="Country")
...     def country(obj,ar):
...         return obj[0]
...     @column(label="City")
...     def city(obj,ar):
...         return obj[1]
...     @column(label="Population")
...     def city(obj,ar):
...         return obj[2]
...

>>> CitiesAndInhabitants.request().render_to_html()

"""

import yaml

from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from lino.core import actors
from lino.core import actions
from lino.core.fields import FakeField
from lino.ui import base
from lino.ui import requests as ext_requests
from lino.utils import perms
from lino.utils.config import Configured, load_config_files


class InvalidRequest(Exception):
    pass


class GridConfig(Configured):
  
    def __init__(self,report,data,*args,**kw):
        self.report = report
        self.data = data
        self.label_en = data.get('label')
        self.data.update(label=_(self.label_en))
        super(GridConfig,self).__init__(*args,**kw)
        must_save = self.validate()
        if must_save:
            msg = self.save_config()
            #~ msg = self.save_grid_config()
            logger.debug(msg)
  
    def validate(self):
        """
        Removes unknown columns
        """
        must_save = False
        gc = self.data
        columns = gc['columns']
        col_count = len(columns)
        widths = gc.get('widths',None)
        hiddens = gc.get('hiddens',None)
        if widths is None:
            widths = [None for x in columns]
            gc.update(widths=widths)
        elif col_count != len(widths):
            raise Exception("%d columns, but %d widths" % (col_count,len(widths)))
        if hiddens is None:
            hiddens = [False for x in columns]
            gc.update(hiddens=hiddens)
        elif col_count != len(hiddens):
            raise Exception("%d columns, but %d hiddens" % (col_count,len(hiddens)))
            
        valid_columns = []
        valid_widths = []
        valid_hiddens = []
        for i,colname in enumerate(gc['columns']):
            f = self.report.get_data_elem(colname)
            if f is None:
                logger.debug("Removed unknown column %d (%r). Must save.",i,colname)
                must_save = True
            else:
                valid_columns.append(colname)
                valid_widths.append(widths[i])
                valid_hiddens.append(hiddens[i])
        gc.update(widths=valid_widths)
        gc.update(hiddens=valid_hiddens)
        gc.update(columns=valid_columns)
        return must_save
            
    def unused_write_content(self,f):
        self.data.update(label=self.label_en)
        f.write(yaml.dump(self.data))
        self.data.update(label=_(self.label_en))
        
    def write_content(self,f):
        f.write(yaml.dump(self.data))
        
        




class AbstractTableRequest(actions.ActionRequest):
    
    limit = None
    offset = None
    create_rows = None
    
    #~ def __init__(self,ui,report,request,action,*args,**kw):
    def __init__(self,ui,report,request,action,**kw):
        if not (isinstance(report,type) and issubclass(report,AbstractTable)):
            raise Exception("Expected an AbstractTable subclass, got %r" % report)
        #~ reports.ReportActionRequest.__init__(self,rh.ui,rh.report,action)
        actions.ActionRequest.__init__(self,ui,report,request,action,**kw)
        #~ self.setup(*args,**kw)
        self.data_iterator = self.get_data_iterator()
        self.sliced_data_iterator = self.data_iterator
        if self.offset is not None:
            self.sliced_data_iterator = self.sliced_data_iterator[self.offset:]
        if self.limit is not None:
            self.sliced_data_iterator = self.sliced_data_iterator[:self.limit]
        
        
    
    def parse_req(self,request,rqdata,**kw):
        rh = self.ah
        kw = actions.ActionRequest.parse_req(self,request,rqdata,**kw)
        #~ raise Exception("20120121 %s.parse_req(%s)" % (self,kw))
        
        #~ kw.update(self.report.known_values)
        #~ for fieldname, default in self.report.known_values.items():
            #~ v = request.REQUEST.get(fieldname,None)
            #~ if v is not None:
                #~ kw[fieldname] = v
                
        quick_search = rqdata.get(ext_requests.URL_PARAM_FILTER,None)
        if quick_search:
            kw.update(quick_search=quick_search)
            
        sort = rqdata.get(ext_requests.URL_PARAM_SORT,None)
        if sort:
            #~ self.sort_column = sort
            sort_dir = rqdata.get(ext_requests.URL_PARAM_SORTDIR,'ASC')
            if sort_dir == 'DESC':
                sort = '-' + sort
                #~ self.sort_direction = 'DESC'
            kw.update(order_by=[sort])
        
                
        offset = rqdata.get(ext_requests.URL_PARAM_START,None)
        if offset:
            kw.update(offset=int(offset))
        limit = rqdata.get(ext_requests.URL_PARAM_LIMIT,None)
        if limit:
            kw.update(limit=int(limit))
        
        
        #~ kw.update(param_values=request.REQUEST.getlist(ext_requests.URL_PARAM_PARAM_VALUES))
        
        #~ def parse_param(fld,request,kv):
            #~ v = request.REQUEST.get(fld.name,None)
            #~ if v is not None:
                #~ kv[fld.name] = v
            
        #~ kv = kw.get('known_values',{})
        #~ for fld in self.report.params:
            #~ parse_param(fld,request,kv)
        #~ if kv:
            #~ kw.update(known_values=kv)
        
        return rh.report.parse_req(request,rqdata,**kw)
        
            
    def setup(self,
            quick_search=None,
            order_by=None,
            offset=None,limit=None,
            **kw):
            
        self.quick_search = quick_search
        self.order_by = order_by
        
    #~ if user is not None and not self.report.can_view.passes(user):
            #~ msg = _("User %(user)s cannot view %(report)s.") % dict(user=user,report=self.report)
            #~ raise InvalidRequest(msg)
            
        #~ if user is None:
            #~ raise InvalidRequest("%s : user is None" % self)
            
        actions.ActionRequest.setup(self,**kw)
        if offset is not None:
            self.offset = offset
            
        if limit is not None:
            self.limit = limit
        
        self.report.setup_request(self)
        
        
    def spawn_request(self,rpt,**kw):
        #~ rh = rpt.get_handle(self.ui)
        kw.update(user=self.user)
        kw.update(renderer=self.renderer)
        #~ return ViewReportRequest(None,rh,rpt.default_action,**kw)
        return self.__class__(self.ui,rpt,None,rpt.default_action,**kw)
        
    def get_status(self,ui,**kw):
        kw = actions.ActionRequest.get_status(self,ui,**kw)
        bp = kw.setdefault('base_params',{})
        if self.subst_user is not None:
            bp[ext_requests.URL_PARAM_SUBST_USER] = self.subst_user.username
            
        if self.quick_search:
            bp[ext_requests.URL_PARAM_FILTER] = self.quick_search
            
        if self.known_values:
            #~ kv = dict()
            for k,v in self.known_values.items():
                if self.report.known_values.get(k,None) != v:
                    bp[k] = v
            #~ kw.update(known_values = kv)
                
            #~ kw[ext_requests.URL_PARAM_KNOWN_VALUES] = self.known_values
        return kw
            
    def get_data_iterator(self):
        if self.report.get_data_rows:
            l = []
            for row in self.report.get_data_rows(self):
                group = self.report.group_from_row(row)
                group.process_row(l,row)
            return l
        return self.report.get_request_queryset(self)
        
    def get_total_count(self):
        """
        Calling `len()` on a QuerySet will execute the whole SELECT.
        See :doc:`/blog/2012/0124`
        """
        if isinstance(self.data_iterator,QuerySet):
            return self.data_iterator.count()
        return len(self.data_iterator)
        
        
        
class VirtualTableRequest(AbstractTableRequest):
    pass
        
    #~ def setup(self,**kw):
        #~ AbstractTableRequest.setup(self,**kw)
        #~ self.total_count = len(self._data_iterator)




class TableHandle(base.Handle): 
  
    _layouts = None
    
    def __init__(self,ui,report):
        self.report = report
        base.Handle.__init__(self,ui)
  
    def __str__(self):
        return str(self.report) + 'Handle'
            
    def setup_layouts(self):
        if self._layouts is not None:
            return
        self._layouts = [ self.list_layout ] 
              
    def get_actor_url(self,*args,**kw):
        return self.ui.get_actor_url(self.report,*args,**kw)
        
    def submit_elems(self):
        return []
        
    def get_list_layout(self):
        self.setup_layouts()
        return self._layouts[0]
        
    def get_columns(self):
        lh = self.get_list_layout()
        #~ print 20110315, layout._main.columns
        return lh.main.columns
        
    def get_slaves(self):
        return [ sl.get_handle(self.ui) for sl in self.report._slaves ]
            
    def get_action(self,name):
        return self.report.get_action(name)
    def get_actions(self,*args,**kw):
        return self.report.get_actions(*args,**kw)
        
    def update_detail(self,tab,desc):
        #~ raise Exception("Not yet fully converted to Lino 1.3.0")
        old_dl = self.report.get_detail().layouts[tab]
        dtl = DetailLayout(desc,old_dl.filename,old_dl.cd)
        self.report.get_detail().layouts[tab] = dtl
        #~ dh = dtl.get_handle(self.ui)
        #~ self._layouts[tab+1] = LayoutHandle(self.ui,self.report.model,dtl)
        self.ui.setup_handle(self)
        #~ self.report.save_config()
        dtl.save_config()

class Group(object):
  
    def __init__(self):
        self.sums = []
        
    def process_row(self,collector,row):
        collector.append(row)

    #~ def add_to_table(self,table):
        #~ self.table = table
        #~ for col in table.computed_columns.values():




class AbstractTable(actors.Actor):
    """
    Base class for :class:`Table` and `VirtualTable`.
    
    An AbstractTable is the definition of a tabular data view, 
    usually displayed in a Grid (but it's up to the user 
    interface to decide how to implement this).
    
    The `column_names` attribute defines the "horizontal layout".
    The "vertical layout" is some iterable.
    """
    _handle_class = TableHandle
    
    #~ field = None
    
    column_names = '*'
    """
    A string that describes the list of columns of this table.
    """
    
    group_by = None
    """
    A list of field names that define the groups of rows in this table.
    Each group can have her own header and/or total lines.
    """
    
    custom_groups = []
    """
    Used internally to store :class:`groups <Group>` defined by this Table.
    """
    
    get_data_rows = None
    """
    Custom tables must define a class method of this name which 
    will be called with a TableRequest object and which is expected
    to return or yield the list of "rows"::
    
        @classmethod
        def get_data_rows(self,request):
            ...
            yield somerow
            
    Model tables may also define such a method in case they need local filtering.
    
    """
    
    #~ column_defaults = {}
    #~ """
    #~ A dictionary of default parameters for :class:`computed columns <ComputedColumn>` on this table.
    #~ """
    
    #~ hide_columns = None
    hidden_columns = frozenset()
    form_class = None
    help_url = None
    #master_instance = None
    
    page_length = 20
    """
    Number of rows to display per page.
    """
    
    cell_edit = True 
    """
    `True` to use ExtJS CellSelectionModel, `False` to use RowSelectionModel.
    """
    
    #~ date_format = lino.DATE_FORMAT_EXTJS
    #~ boolean_texts = boolean_texts
    boolean_texts = boolean_texts = (_('Yes'),_('No'),' ')
    
    #~ can_view = perms.always
    #~ can_change = perms.is_authenticated
    #~ can_config = perms.is_staff
    
    #~ show_prev_next = True
    show_detail_navigator = False
    """
    Whether a Detail view on a row of this table should feature a navigator
    """
    
    default_group = Group()
    
    
    #~ default_action = GridEdit
    default_layout = 0
    
    typo_check = True
    """
    True means that Lino shoud issue a warning if a subclass 
    defines any attribute that did not exist in the base class.
    Usually such a warning means that there is something wrong.
    """
    
    #~ url = None
    
    #~ use_layouts = True
    
    button_label = None
    
    slave_grid_format = 'grid'
    """
    How to display this table when it is a slave in a detail window. 
    `grid` (default) to render as a grid. 
    `summary` to render a summary in a HtmlBoxPanel.
    `html` to render plain html  a HtmlBoxPanel.
    Example: :class:`links.LinksByOwner`
    """
    
    grid_configs = []
    """
    Will be filled during :meth:`lino.core.table.Table.do_setup`. 
    """
    
    editable = None
    """
    Set this explicitly to True or False to make the 
    table per se editable or not.
    Otherwise it will be set to `False` if the table has a `get_data_rows` method
    """
    
    
    def __init__(self,*args,**kw):
        raise NotImplementedError("20120104")
    
    @classmethod
    def spawn(cls,suffix,**kw):
        kw['app_label'] = cls.app_label
        return type(cls.__name__+str(suffix),(cls,),kw)
        
          
    @classmethod
    def parse_req(self,request,rqdata,**kw):
        return kw
    
    @classmethod
    def do_setup(self):
      
        if self.get_data_rows is not None:
            self.show_detail_navigator = False
            
        if self.editable is None:
            self.editable = (self.get_data_rows is None)
      
        self.setup_columns()
        
        super(AbstractTable,self).do_setup()
        
        self.grid_configs = []
        
        def loader(content,cd,filename):
            data = yaml.load(content)
            gc = GridConfig(self,data,filename,cd)
            self.grid_configs.append(gc)
            
        load_config_files(loader,'%s.*gc' % self)
        
        self.default_action = actions.GridEdit(self) # 20120220 
        #~ self.setup_detail_layouts()
        #~ self.set_actions([])
        self.add_action(self.default_action)
        self.setup_actions()
        #~ if self.default_action.actor != self:
            #~ raise Exception("20120103 %r.do_setup() : default.action.actor is %r" % (
              #~ self,self.default_action.actor))
                
        if self.button_label is None:
            self.button_label = self.label
            
        
    @classmethod
    def setup_columns(self):
        pass
        
    #~ @classmethod
    #~ def add_column(self,*args,**kw):
        #~ """
        #~ Use this from an overridden `before_ui_handle` method to 
        #~ dynamically define computed columns to this table.
        #~ """
        #~ return self._add_column(ComputedColumn(*args,**kw))
        
    #~ @classmethod
    #~ def _add_column(self,col):
        #~ col.add_to_table(self)
        #~ # make sure we don't add it to an inherited `computed_columns`:
        #~ self.computed_columns = dict(self.computed_columns)
        #~ self.computed_columns[col.name] = col
        #~ return col
      
    @classmethod
    def group_from_row(self,row):
        return self.default_group
    
    @classmethod
    def wildcard_data_elems(self):
        for cc in self.virtual_fields.values():
            yield cc
        #~ return []
        
    #~ @classmethod
    #~ def get_detail(self):
        #~ return None
        
    @classmethod
    def get_permission(self,action,user,obj):
        if self.get_data_rows:
            return action.readonly
        return True
        
        
    @classmethod
    def save_grid_config(self,index,data):
        if len(self.grid_configs) == 0:
            gc = GridConfig(self,data,'%s.gc' % self)
            self.grid_configs.append(gc)
        else:
            gc = self.grid_configs[index]
        gc.data = data
        gc.validate()
        #~ self.grid_configs[index] = gc
        return gc.save_config()
        #~ filename = self.get_grid_config_file(gc)
        #~ f = open(filename,'w')
        #~ f.write("# Generated file. Delete it to restore default configuration.\n")
        #~ d = dict(grid_configs=self.grid_configs)
        #~ f.write(yaml.dump(d))
        #~ f.close()
        #~ return "Grid Config has been saved to %s" % filename
    
    @classmethod
    def slave_as_html_meth(self,ui):
        """
        Creates and returns the method to be used when 
        :attr:`AbstractTable.slave_grid_format` is `html`.
        """
        def meth(master,ar):
            ar = self.request(ui,request=ar.request,
                action=self.default_action,master_instance=master)
            ar.renderer = ui.ext_renderer
            #~ ar = TableRequest(ui,self,None,self.default_action,master_instance=master)
            s = ui.table2xhtml(ar).tostring()
            return s
        return meth


class VirtualTable(AbstractTable):
    """
    An :class:`AbstractTable` that works on an 
    volatile (non persistent) list of rows.
    By nature it cannot have database fields, only virtual fields.
    """
    
    @classmethod
    def request(cls,ui=None,request=None,action=None,**kw):
        self = cls
        if action is None:
            action = self.default_action
        return VirtualTableRequest(ui,self,request,action,**kw)





