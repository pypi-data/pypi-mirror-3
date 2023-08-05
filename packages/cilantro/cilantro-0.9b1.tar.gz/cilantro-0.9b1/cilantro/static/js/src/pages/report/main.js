require(['cilantro/types/report/main', 'cilantro/report/table', 'cilantro/report/columns'], function(Report, m_table, m_columns) {
  var sessionReport;
  sessionReport = new Report.Models.Session;
  App.hub.subscribe('session/idle', function() {
    return sessionReport.stopPolling();
  });
  App.hub.subscribe('session/resume', function() {
    return sessionReport.startPolling();
  });
  return $(function() {
    var ReportEditor, ReportName, UnsavedReport, e;
    ReportEditor = new Report.Views.Editor;
    ReportName = new Report.Views.Name({
      model: sessionReport
    });
    UnsavedReport = new Report.Messages.UnsavedReport({
      model: sessionReport
    });
    sessionReport.fetch();
    m_columns.init();
    m_table.init();
    e = $('#export-data');
    return e.bind('click', function() {
      e.attr('disabled', true);
      window.location = App.urls.session.report + '?data=1&format=csv';
      setTimeout(function() {
        return e.attr('disabled', false);
      }, 5000);
      return false;
    });
  });
});