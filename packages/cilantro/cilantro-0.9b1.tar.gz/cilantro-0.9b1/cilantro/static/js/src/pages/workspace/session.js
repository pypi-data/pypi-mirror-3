var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
  for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
  function ctor() { this.constructor = child; }
  ctor.prototype = parent.prototype;
  child.prototype = new ctor;
  child.__super__ = parent.prototype;
  return child;
};
define(['common/views/collection'], function(CollectionViews) {
  var PerspectiveView, ReportView, ScopeView;
  ScopeView = (function() {
    __extends(ScopeView, CollectionViews.ExpandableList);
    function ScopeView() {
      this.render = __bind(this.render, this);
      ScopeView.__super__.constructor.apply(this, arguments);
    }
    ScopeView.prototype.el = '#session-scope';
    ScopeView.prototype.defaultContent = '<li class="info">No conditions have been defined</li>';
    ScopeView.prototype.initialize = function() {
      this.model.bind('change:conditions', this.render);
      this.defaultContent = this.$(this.defaultContent);
      return this.el.append(this.defaultContent);
    };
    ScopeView.prototype.render = function() {
      var conditions, text;
      conditions = this.model.get('conditions');
      this.defaultContent.detach();
      this.el.empty();
      if (conditions) {
        text = '';
        _.map(conditions, function(node) {
          return text += "<li>" + node.condition + "</li>";
        });
        this.el.html(text);
      } else {
        this.el.append(this.defaultContent);
      }
      return this.collapse();
    };
    return ScopeView;
  })();
  PerspectiveView = (function() {
    __extends(PerspectiveView, CollectionViews.ExpandableList);
    function PerspectiveView() {
      this.render = __bind(this.render, this);
      PerspectiveView.__super__.constructor.apply(this, arguments);
    }
    PerspectiveView.prototype.el = '#session-perspective';
    PerspectiveView.prototype.defaultContent = '<li class="info">No data columns have been choosen</li>';
    PerspectiveView.prototype.initialize = function() {
      this.model.bind('change:header', this.render);
      this.defaultContent = this.$(this.defaultContent);
      return this.el.append(this.defaultContent);
    };
    PerspectiveView.prototype.template = _.template('<li><%= name %><% if (direction) { %>\
                <span class="info">(<%= direction %>)</span><% } %></li>');
    PerspectiveView.prototype.render = function() {
      var col, header, _i, _len;
      this.defaultContent.detach();
      this.el.empty();
      if ((header = this.model.get('header'))) {
        for (_i = 0, _len = header.length; _i < _len; _i++) {
          col = header[_i];
          this.el.append(this.template(col));
        }
      } else {
        this.el.append(this.defaultContent);
      }
      return this.collapse();
    };
    return PerspectiveView;
  })();
  ReportView = (function() {
    __extends(ReportView, Backbone.View);
    function ReportView() {
      this.render = __bind(this.render, this);
      ReportView.__super__.constructor.apply(this, arguments);
    }
    ReportView.prototype.el = '#session-report';
    ReportView.prototype.elements = {
      '[role=name]': 'name',
      '[role=modified]': 'modified',
      '[role=timesince]': 'timesince'
    };
    ReportView.prototype.events = {
      'click .timestamp': 'toggleTime'
    };
    ReportView.prototype.initialize = function() {
      return this.model.bind('change', this.render);
    };
    ReportView.prototype.render = function() {
      if (this.model.hasChanged('name')) {
        this.name.text(this.model.get('name')).attr('href', this.model.get('permalink')).parent().show();
      } else if (!this.model.get('name')) {
        this.name.parent().hide();
      }
      this.modified.text(this.model.get('modified'));
      return this.timesince.text(this.model.get('timesince'));
    };
    ReportView.prototype.toggleTime = function() {
      this.modified.toggle();
      return this.timesince.toggle();
    };
    return ReportView;
  })();
  return {
    Report: ReportView,
    Scope: ScopeView,
    Perspective: PerspectiveView
  };
});