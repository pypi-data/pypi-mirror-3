var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

define(['backbone', 'common/models/polling'], function(Backbone, polling) {
  var createObjectSetClasses, createObjectSetPair;
  createObjectSetClasses = function(configs) {
    var classes, config, _i, _len;
    classes = [];
    for (_i = 0, _len = configs.length; _i < _len; _i++) {
      config = configs[_i];
      classes.push(createObjectSetPair(config));
    }
    return classes;
  };
  createObjectSetPair = function(config) {
    var Collection, Model;
    Model = (function() {

      __extends(Model, Backbone.Model);

      function Model() {
        Model.__super__.constructor.apply(this, arguments);
      }

      Model.prototype.url = function() {
        var url;
        url = Model.__super__.url.apply(this, arguments);
        if (!/\/$/.test(url)) url += '/';
        return url;
      };

      Model.prototype.initialize = function() {
        return this.bind('change', function() {
          return App.hub.publish("" + config.name + "/change", this);
        });
      };

      return Model;

    })();
    Collection = (function() {

      __extends(Collection, polling.Collection);

      function Collection() {
        Collection.__super__.constructor.apply(this, arguments);
      }

      Collection.prototype.name = "" + config.name + " Sets";

      Collection.prototype.url = config.url;

      Collection.prototype.model = Model;

      Collection.prototype.comparator = function(model) {
        return -Number(new Date(model.get('modified')));
      };

      return Collection;

    })();
    return {
      Model: Model,
      Collection: Collection
    };
  };
  return {
    createObjectSetClasses: createObjectSetClasses
  };
});
