define(['jquery', 'underscore', 'backbone', 'pubsub', 'common/utils'], function($, _, Backbone, PubSub, Utils) {
  var App, attrs;
  this.$ = this.jQuery = $;
  attrs = this.App || {};
  attrs.hub = new PubSub;
  attrs.Models = {};
  attrs.Collections = {};
  attrs.Views = {};
  return this.App = App = new Utils.App(attrs);
});