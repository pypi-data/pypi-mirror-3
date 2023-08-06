var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

define(['backbone', 'cilantro/views'], function(Backbone, Views) {
  var ObjectSetEditor, ObjectSetItem, ObjectSetList;
  ObjectSetEditor = (function() {

    __extends(ObjectSetEditor, Views.Dialog.ItemEditor);

    function ObjectSetEditor() {
      ObjectSetEditor.__super__.constructor.apply(this, arguments);
    }

    ObjectSetEditor.prototype.initialize = function() {
      App.hub.subscribe('object-set/edit', this.editHandler);
      return ObjectSetEditor.__super__.initialize.apply(this, arguments);
    };

    return ObjectSetEditor;

  })();
  ObjectSetItem = (function() {

    __extends(ObjectSetItem, Views.List.Item);

    function ObjectSetItem() {
      ObjectSetItem.__super__.constructor.apply(this, arguments);
    }

    ObjectSetItem.prototype.className = 'object-set';

    ObjectSetItem.prototype.edit = function(evt, model) {
      if (model == null) model = this.model;
      App.hub.publish('object-set/edit', model);
      return false;
    };

    return ObjectSetItem;

  })();
  ObjectSetList = (function() {

    __extends(ObjectSetList, Views.List.List);

    function ObjectSetList() {
      ObjectSetList.__super__.constructor.apply(this, arguments);
    }

    ObjectSetList.prototype.viewClass = ObjectSetItem;

    ObjectSetList.prototype.defaultContent = '<section class="info">You have no saved sets.</section>';

    return ObjectSetList;

  })();
  return {
    Item: ObjectSetItem,
    List: ObjectSetList,
    Editor: ObjectSetEditor
  };
});
