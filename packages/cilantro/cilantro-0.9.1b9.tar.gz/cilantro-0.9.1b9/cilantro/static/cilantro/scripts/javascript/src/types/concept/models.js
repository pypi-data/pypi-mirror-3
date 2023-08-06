var __hasProp = Object.prototype.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

define(['underscore', 'backbone', 'common/models/state'], function(_, Backbone, statemodel) {
  /*
      Concepts are the data-driven entry points for constructing their
      self-contained interfaces. Every concept must be "contained" within
      a domain, thus when a concept becomes active, the associated domain
      (or sub-domain) will become active as well.
  */
  var Concept, ConceptCollection;
  Concept = (function(_super) {

    __extends(Concept, _super);

    function Concept() {
      Concept.__super__.constructor.apply(this, arguments);
    }

    Concept.prototype.url = function() {
      return Concept.__super__.url.apply(this, arguments) + '/';
    };

    return Concept;

  })(statemodel.Model);
  /*
      The ConceptCollection encapsulates cross-instance logic.
  */
  ConceptCollection = (function(_super) {

    __extends(ConceptCollection, _super);

    function ConceptCollection() {
      this.toggleEnableByDomain = __bind(this.toggleEnableByDomain, this);
      ConceptCollection.__super__.constructor.apply(this, arguments);
    }

    ConceptCollection.prototype.model = Concept;

    ConceptCollection.prototype.url = App.endpoints.criteria;

    ConceptCollection.prototype.initialize = function() {
      var _this = this;
      App.hub.subscribe('domain/active', this.toggleEnableByDomain);
      App.hub.subscribe('subdomain/active', this.toggleEnableByDomain);
      this.bind('reset', this.groupByDomain);
      this.bind('active', this.activate);
      this.bind('inactive', this.inactivate);
      App.hub.subscribe('concept/request', function(id) {
        var concept;
        concept = _this.get(id);
        if (concept) {
          App.hub.publish('domain/request', concept.get('domain').id);
          return concept.activate();
        }
      });
      this._activeByDomain = {};
      return this._activeDomain = null;
    };

    ConceptCollection.prototype.groupByDomain = function() {
      var _this = this;
      this._byDomain = {};
      this._bySubdomain = {};
      return this.each(function(model) {
        var domain, _base, _base2, _base3, _name, _name2, _name3, _ref, _ref2, _ref3;
        domain = model.get('domain');
        if (domain.parent) {
          ((_ref = (_base = _this._bySubdomain)[_name = domain.id]) != null ? _ref : _base[_name] = []).push(model);
          return ((_ref2 = (_base2 = _this._byDomain)[_name2 = domain.parent.id]) != null ? _ref2 : _base2[_name2] = []).push(model);
        } else {
          return ((_ref3 = (_base3 = _this._byDomain)[_name3 = domain.id]) != null ? _ref3 : _base3[_name3] = []).push(model);
        }
      });
    };

    ConceptCollection.prototype.toggleEnableByDomain = function(id) {
      var concepts, model;
      this._activeDomain = id;
      concepts = this._bySubdomain[id] || this._byDomain[id];
      this.map(function(model) {
        if (__indexOf.call(concepts, model) >= 0) {
          model.enable();
          return model.inactivate();
        } else {
          return model.disable();
        }
      });
      if ((model = this._activeByDomain[id])) return model.activate();
    };

    ConceptCollection.prototype.activate = function(model) {
      var concepts;
      this._activeByDomain[this._activeDomain] = model;
      concepts = this._bySubdomain[this._activeDomain] || this._byDomain[this._activeDomain];
      return _(concepts).without(model).map(function(model) {
        return model.inactivate();
      });
    };

    ConceptCollection.prototype.inactivate = function(model) {};

    return ConceptCollection;

  })(Backbone.Collection);
  return {
    Model: Concept,
    Collection: ConceptCollection
  };
});
