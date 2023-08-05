var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
  for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
  function ctor() { this.constructor = child; }
  ctor.prototype = parent.prototype;
  child.prototype = new ctor;
  child.__super__ = parent.prototype;
  return child;
};
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
    return Report;
  })();
  ReportCollection = (function() {
    __extends(ReportCollection, polling.Collection);
    function ReportCollection() {
      ReportCollection.__super__.constructor.apply(this, arguments);
    }
    ReportCollection.prototype.url = App.urls.reports;
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
    SessionReport.prototype.url = App.urls.session.report;
    SessionReport.prototype.defaults = {
      name: 'click to add a name...',
      description: 'click to add a description...'
    };
    return SessionReport;
  })();
  return {
    Model: Report,
    Collection: ReportCollection,
    Session: SessionReport
  };
});