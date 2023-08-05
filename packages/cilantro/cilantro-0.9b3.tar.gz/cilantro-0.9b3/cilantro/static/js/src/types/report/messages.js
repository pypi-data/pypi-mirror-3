var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
  for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
  function ctor() { this.constructor = child; }
  ctor.prototype = parent.prototype;
  child.prototype = new ctor;
  child.__super__ = parent.prototype;
  return child;
}, __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
define(['cilantro/utils/logging'], function(Logging) {
  var UnsavedReport, templates;
  templates = {
    UnsavedReportTemplate: '<div class="message-block warning">\
                    <div class="content">\
                        <strong role="name"><%= name %></strong> has unsaved changes\
                    </div>\
                    <button class="revert">Revert</button>\
                    <button class="save">Save</button>\
                </div>'
  };
  UnsavedReport = (function() {
    __extends(UnsavedReport, Logging.MessageView);
    function UnsavedReport() {
      UnsavedReport.__super__.constructor.apply(this, arguments);
    }
    UnsavedReport.prototype.template = _.template(templates.UnsavedReportTemplate);
    UnsavedReport.prototype.elements = {
      '[role=name]': 'name'
    };
    UnsavedReport.prototype.events = {
      'click .save': 'save',
      'click .cancel': 'cancel'
    };
    UnsavedReport.prototype.initialize = function() {
      this.render();
      this.model.bind('change:name', __bind(function(model, value) {
        return this.el.find('[role=name]').text(value);
      }, this));
      return this.model.bind('change:has_changed', __bind(function(model, value) {
        if (value) {
          return App.hub.publish('log', this);
        } else {
          return App.hub.publish('dismiss', this);
        }
      }, this));
    };
    UnsavedReport.prototype.render = function() {
      this.el = $(this.template(this.model.toJSON()));
      this.setLocalElements();
      this.delegateEvents();
      return this;
    };
    UnsavedReport.prototype.save = function() {
      return this.model.save(null, {
        url: this.model.get('permalink')
      });
    };
    UnsavedReport.prototype.cancel = function() {};
    return UnsavedReport;
  })();
  return {
    UnsavedReport: UnsavedReport,
    templates: templates
  };
});