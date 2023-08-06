var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = Object.prototype.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

define(['common/models/polling'], function(polling) {
  var SessionPerspective;
  SessionPerspective = (function(_super) {

    __extends(SessionPerspective, _super);

    function SessionPerspective() {
      this.revert = __bind(this.revert, this);
      SessionPerspective.__super__.constructor.apply(this, arguments);
    }

    SessionPerspective.prototype.url = App.endpoints.session.perspective;

    SessionPerspective.prototype.initialize = function() {
      SessionPerspective.__super__.initialize.apply(this, arguments);
      return App.hub.subscribe('report/revert', this.revert);
    };

    SessionPerspective.prototype.revert = function() {
      return this.fetch();
    };

    return SessionPerspective;

  })(polling.Model);
  return {
    Session: SessionPerspective
  };
});
