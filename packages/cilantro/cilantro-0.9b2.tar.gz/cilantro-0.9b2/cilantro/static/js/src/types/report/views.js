var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
  for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
  function ctor() { this.constructor = child; }
  ctor.prototype = parent.prototype;
  child.prototype = new ctor;
  child.__super__ = parent.prototype;
  return child;
};
define(['common/utils', 'common/views/collection'], function(utils, CollectionViews) {
  var ReportEditor, ReportEditorMixin, ReportItem, ReportList, ReportName;
  ReportEditor = (function() {
    __extends(ReportEditor, Backbone.View);
    function ReportEditor() {
      this.editHandler = __bind(this.editHandler, this);
      ReportEditor.__super__.constructor.apply(this, arguments);
    }
    ReportEditor.prototype.el = '<div id="report-editor">\
                <input type="text" name="name" placeholder="Name...">\
                <textarea name="description" placeholder="Description..."></textarea>\
                <div class="controls">\
                    <button class="cancel">Cancel</button>\
                    <button class="save">Save</button>\
                </div>\
            </div>';
    ReportEditor.prototype.elements = {
      '[name=name]': 'name',
      '[name=description]': 'description',
      '.save': 'saveButton',
      '.cancel': 'cancelButton'
    };
    ReportEditor.prototype.events = {
      'click .save': 'save',
      'click .cancel': 'cancel'
    };
    ReportEditor.prototype.initialize = function() {
      App.hub.subscribe('report/edit', this.editHandler);
      return this.el.appendTo('body').dialog({
        dialogClass: 'ui-dialog-simple',
        autoOpen: false,
        modal: true,
        resizable: false,
        draggable: true,
        position: ['center', 150],
        width: 500
      });
    };
    ReportEditor.prototype.editHandler = function(model) {
      this.name.val(model.get('name'));
      this.description.val(model.get('description'));
      this.activeModel = model;
      return this.el.dialog('open');
    };
    ReportEditor.prototype.save = function() {
      this.activeModel.set({
        name: this.name.val(),
        description: this.description.val()
      });
      this.activeModel.save();
      if (this.activeModel.isNew()) {
        this.activeModel.collection.add(this.activeModel);
      }
      delete this.activeModel;
      return this.el.dialog('close');
    };
    ReportEditor.prototype.cancel = function() {
      delete this.activeModel;
      return this.el.dialog('close');
    };
    return ReportEditor;
  })();
  ReportEditorMixin = {
    edit: function(evt, model) {
      if (model == null) {
        model = this.model;
      }
      App.hub.publish('report/edit', model);
      return false;
    }
  };
  ReportItem = (function() {
    __extends(ReportItem, Backbone.View);
    function ReportItem() {
      ReportItem.__super__.constructor.apply(this, arguments);
    }
    ReportItem.prototype.el = '<section class="report">\
                    <a role="name"></a>\
                    <span class="info">- <span role="unique-count"></span> unique patients</span>\
                    <span class="info time" style="float: right">modified <span role="modified"></span><span role="timesince"></span></span>\
                    <div role="description"></div>\
                    <div class="controls">\
                        <button class="delete">Delete</button>\
                        <button class="edit">Edit</button>\
                        <button class="copy">Copy</button>\
                    </div>\
                </section>';
    ReportItem.prototype.events = {
      'click .time': 'toggleTime',
      'click .edit': 'edit',
      'click .copy': 'copy',
      'click .delete': 'delete',
      'mouseenter': 'showControls',
      'mouseleave': 'hideControls'
    };
    ReportItem.prototype.elements = {
      '[role=name]': 'name',
      '[role=unique-count]': 'uniqueCount',
      '[role=modified]': 'modified',
      '[role=timesince]': 'timesince',
      '[role=description]': 'description',
      '.controls': 'controls'
    };
    ReportItem.prototype.render = function() {
      var description;
      this.name.text(this.model.get('name'));
      this.name.attr('href', this.model.get('permalink'));
      this.modified.text(this.model.get('modified'));
      this.timesince.text(this.model.get('timesince'));
      if (!(description = this.model.get('description'))) {
        description = 'No description provided';
      }
      this.description.text(description);
      this.uniqueCount.text(this.model.get('unique_count'));
      return this;
    };
    ReportItem.prototype.toggleTime = function(evt) {
      this.modified.toggle();
      this.timesince.toggle();
      return evt.stopPropagation();
    };
    ReportItem.prototype.showControls = function(evt) {
      this._controlsTimer = setTimeout(__bind(function() {
        return this.controls.slideDown(200);
      }, this), 300);
      return false;
    };
    ReportItem.prototype.hideControls = function(evt) {
      clearTimeout(this._controlsTimer);
      this.controls.slideUp(300);
      return false;
    };
    ReportItem.prototype.copy = function(evt) {
      var copy;
      copy = this.model.clone();
      copy.set('id', null);
      copy.set('name', copy.get('name') + ' (copy)');
      copy.set('_id', this.model.id);
      copy.collection = this.model.collection;
      this.edit(evt, copy);
      return false;
    };
    ReportItem.prototype["delete"] = function() {
      return this.model.destroy();
    };
    return ReportItem;
  })();
  ReportList = (function() {
    __extends(ReportList, CollectionViews.View);
    function ReportList() {
      ReportList.__super__.constructor.apply(this, arguments);
    }
    ReportList.prototype.el = '#report-list';
    ReportList.prototype.viewClass = ReportItem;
    ReportList.prototype.defaultContent = '<section class="info">You have no saved reports.</section>';
    return ReportList;
  })();
  ReportName = (function() {
    __extends(ReportName, Backbone.View);
    function ReportName() {
      this.render = __bind(this.render, this);
      ReportName.__super__.constructor.apply(this, arguments);
    }
    ReportName.prototype.el = '#report-name';
    ReportName.prototype.events = {
      'click': 'edit',
      'mouseover': 'hover',
      'mouseout': 'hover'
    };
    ReportName.prototype.initialize = function(options) {
      this.model.bind('change:name', this.render);
      return this.hoverText = $('<span class="info">click to edit</span>');
    };
    ReportName.prototype.render = function() {
      var name;
      this.el.text('');
      if ((name = this.model.get('name'))) {
        this.el.removeClass('placeholder');
        this.el.append(this.hoverText.hide());
      } else {
        this.el.addClass('placeholder');
        name = this.model.defaults.name;
        this.hoverText.detach();
      }
      return this.el.prepend(name + ' ');
    };
    ReportName.prototype.hover = function() {
      return this.hoverText.toggle();
    };
    return ReportName;
  })();
  utils.include(ReportItem, ReportEditorMixin);
  utils.include(ReportList, CollectionViews.ExpandableListMixin);
  utils.include(ReportName, ReportEditorMixin);
  return {
    Name: ReportName,
    Item: ReportItem,
    List: ReportList,
    Editor: ReportEditor
  };
});