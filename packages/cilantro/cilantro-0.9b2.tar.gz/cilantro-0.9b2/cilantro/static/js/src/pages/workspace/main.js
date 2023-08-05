define(['cilantro/types/report/main', 'cilantro/types/scope/main', 'cilantro/types/perspective/main', 'cilantro/pages/workspace/session'], function(Report, Scope, Perspective, Views) {
  var reports, sessionPerspective, sessionReport, sessionScope;
  reports = new Report.Models.Collection;
  sessionReport = new Report.Models.Session;
  sessionScope = new Scope.Models.Session;
  sessionPerspective = new Perspective.Models.Session;
  App.hub.subscribe('session/idle', function() {
    reports.stopPolling();
    sessionReport.stopPolling();
    sessionScope.stopPolling();
    return sessionPerspective.stopPolling();
  });
  App.hub.subscribe('session/resume', function() {
    reports.startPolling();
    sessionReport.startPolling();
    sessionScope.startPolling();
    return sessionPerspective.startPolling();
  });
  return $(function() {
    var ReportEditor, ReportList, SessionPerspective, SessionReport, SessionScope, UnsavedReport;
    ReportEditor = new Report.Views.Editor;
    ReportList = new Report.Views.List({
      collection: reports
    });
    SessionScope = new Views.Scope({
      model: sessionScope
    });
    SessionPerspective = new Views.Perspective({
      model: sessionPerspective
    });
    SessionReport = new Views.Report({
      model: sessionReport
    });
    UnsavedReport = new Report.Messages.UnsavedReport({
      model: sessionReport
    });
    reports.fetch();
    sessionReport.fetch();
    sessionScope.fetch();
    return sessionPerspective.fetch();
  });
});