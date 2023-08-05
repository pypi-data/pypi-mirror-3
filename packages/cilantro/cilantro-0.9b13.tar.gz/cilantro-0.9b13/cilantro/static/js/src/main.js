define(['common/utils', 'cilantro/utils/logging', 'cilantro/lib/jquery.ui', 'cilantro/lib/jquery.block', 'cilantro/lib/jquery.jqote2', 'cilantro/lib/jquery.scrollto', 'cilantro/vendor/jquery.idle', 'cilantro/vendor/underscore', 'cilantro/vendor/backbone', 'cilantro/vendor/pubsub', 'cilantro/utils/ajaxsetup', 'cilantro/utils/extensions', 'cilantro/utils/sanitizer'], function(utils, Logging) {
  var App, attrs;
  if (!window.JSON) {
    require(['cilantro/lib/json2']);
  }
  $.block.defaults.message = null;
  $.block.defaults.css = {};
  $.block.defaults.overlayCSS = {};
  attrs = window.App || {};
  attrs.hub = new PubSub;
  attrs.Models = {};
  attrs.Collections = {};
  attrs.Views = {};
  window.App = App = new utils.App(attrs);
  App.Log = new Logging.Log;
  App.LogView = new Logging.LogView;
  $.idleTimer(10 * 1000);
  return $(document).bind({
    'idle.idleTimer': function() {
      return App.hub.publish('session/idle');
    },
    'active.idleTimer': function() {
      return App.hub.publish('session/resume');
    }
  });
});