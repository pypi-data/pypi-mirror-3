
define(['cilantro/core', 'cilantro/utils/logging', 'order!vendor/jquery.ui', 'order!vendor/jquery.idle', 'order!vendor/jquery.jqote2', 'order!vendor/jquery.block', 'order!vendor/jquery.scrollto', 'order!cilantro/utils/ajaxsetup', 'order!cilantro/utils/extensions', 'order!cilantro/utils/sanitizer'], function(Core, Logging) {
  if (!window.JSON) require(['vendor/json2']);
  $.block.defaults.message = null;
  $.block.defaults.css = {};
  $.block.defaults.overlayCSS = {};
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
