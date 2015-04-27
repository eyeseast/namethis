/* build up a list of names from a starting point */

var Name = Backbone.Model.extend({

    idAttribute: 'name',

    defaults: {
        name: ''
    }
});

var NameSet = Backbone.Collection.extend({

    model: Name,

    getRandomName: function(group, exclude, cb) {
        var self = this;
        var recursed = 0;
        group = group || 'all';
        exclude = exclude || [];
        return $.get('/name/' + group, function(name) {
            if (_.contains(exclude, name)) {
                recursed += 1;
                self.getRandomName(group, exclude, cb);
            } else {
                self.recursed = recursed;
                if (recursed > 0) { console.log(recursed); };
                cb(name);
            }
        });
    },

    append: function(name, options) {
        return this.add({name: name}, options);
    }
});

NameSet.from_array = function(list, options) {
    return new NameSet(list.map(function(name) {
        return { name: name };
    }), options);
}

// views, using Marionette

var NameView = Mn.ItemView.extend({

    className: 'name well',

    id: function() { return this.model.get('name'); },

    template: '#name-template',

    events: {
        'click .close' : 'delete'
    },

    delete: function() {
        //Mn.ItemView.prototype.remove.call(this);
        this.model.collection.remove(this.model);
    }

});

var NameListView = Mn.CollectionView.extend({

    childView: NameView,

    initialize: function(options) {
        // store removed names
        this.removed = new NameSet();
    },

    onRemoveChild: function(view) {
        var collection = this.collection;
        var removed = this.removed;        
        
        removed.add(view.model);
        collection.getRandomName('all', removed.pluck('name'), function(name) {
            collection.append(name);
        });
    }

});