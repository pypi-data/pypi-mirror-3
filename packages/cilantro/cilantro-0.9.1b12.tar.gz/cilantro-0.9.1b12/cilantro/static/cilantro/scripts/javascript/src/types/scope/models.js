var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = Object.prototype.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

define(['common/models/polling'], function(polling) {
  var SessionScope;
  SessionScope = (function(_super) {

    __extends(SessionScope, _super);

    function SessionScope() {
      this.revert = __bind(this.revert, this);
      SessionScope.__super__.constructor.apply(this, arguments);
    }

    SessionScope.prototype.url = App.endpoints.session.scope;

    SessionScope.prototype.initialize = function() {
      SessionScope.__super__.initialize.apply(this, arguments);
      return App.hub.subscribe('report/revert', this.revert);
    };

    SessionScope.prototype.revert = function() {
      return this.fetch();
    };

    return SessionScope;

  })(polling.Model);
  return {
    Session: SessionScope
  };
});
