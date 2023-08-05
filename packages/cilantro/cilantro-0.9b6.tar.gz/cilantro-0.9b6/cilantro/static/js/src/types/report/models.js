var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
  for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
  function ctor() { this.constructor = child; }
  ctor.prototype = parent.prototype;
  child.prototype = new ctor;
  child.__super__ = parent.prototype;
  return child;
}, __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
define(['common/models/polling'], function(polling) {
  var Report, ReportCollection, SessionReport;
  Report = (function() {
    __extends(Report, Backbone.Model);
    function Report() {
      Report.__super__.constructor.apply(this, arguments);
    }
    Report.prototype.url = function() {
      var url;
      if (!/\/$/.test((url = Report.__super__.url.apply(this, arguments)))) {
        url += '/';
      }
      return url;
    };
    Report.prototype.initialize = function() {
      return this.bind('change', function() {
        return App.hub.publish('report/change', this);
      });
    };
    return Report;
  })();
  ReportCollection = (function() {
    __extends(ReportCollection, polling.Collection);
    function ReportCollection() {
      ReportCollection.__super__.constructor.apply(this, arguments);
    }
    ReportCollection.prototype.url = App.endpoints.reports;
    ReportCollection.prototype.model = Report;
    ReportCollection.prototype.comparator = function(model) {
      return -Number(new Date(model.get('modified')));
    };
    return ReportCollection;
  })();
  SessionReport = (function() {
    __extends(SessionReport, polling.Model);
    function SessionReport() {
      SessionReport.__super__.constructor.apply(this, arguments);
    }
    SessionReport.prototype.url = App.endpoints.session.report;
    SessionReport.prototype.defaults = {
      name: 'click to give your report a name...',
      description: 'click to give your report a description...'
    };
    SessionReport.prototype.initialize = function() {
      SessionReport.__super__.initialize.apply(this, arguments);
      App.hub.subscribe('report/clear', __bind(function() {
        this.clear({
          silent: true
        });
        return this.save(null, {
          success: function() {
            return window.location = App.endpoints.define;
          }
        });
      }, this));
      return App.hub.subscribe('report/change', __bind(function(model) {
        if (model.id === this.get('reference_id')) {
          return this.set(model.toJSON());
        }
      }, this));
    };
    SessionReport.prototype.push = function() {
      return this.save(null, {
        url: this.get('permalink'),
        success: function() {
          return App.hub.publish('report/push', this);
        }
      });
    };
    SessionReport.prototype.revert = function() {
      return this.save(null, {
        data: JSON.stringify({
          revert: true
        }),
        contentType: 'application/json',
        success: function() {
          return App.hub.publish('report/revert', this);
        }
      });
    };
    return SessionReport;
  })();
  return {
    Model: Report,
    Collection: ReportCollection,
    Session: SessionReport
  };
});