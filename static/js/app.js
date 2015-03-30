/***
Views for each chunk of the app
***/

var NameRouter = Backbone.Router.extend({

    routes: {
        ':name' : 'setName'
    },

    initialize: function(options) {
        this.form = options.form;
        this.listenTo(this.form, 'name', this.navigate);

        Backbone.history.start();
    },

    setName: function(name) {
        this.form.setName(name);
    }
});


var FormView = Backbone.View.extend({

    events: {
        'click button' : 'onClick',
        'submit' : 'onSubmit'
    },

    initialize: function(options) {
        _.bindAll(this, 'setName');
    },

    onClick: function(e) {
        e.preventDefault();

        if (e.target.value === 'go') {
            return this.onSubmit(e);
        };

        this.getRandomName(e.target.value);
    },

    onSubmit: function(e) {
        var name = this.$el.find('[name=firstname]').val();

        this.setName(name);
    },

    getRandomName: function(group) {
        var form = this;
        group = group || 'all';

        $.get('/name/' + group, this.setName);
    },

    getNameStats: function(name) {
        var form = this;
        $.get('/' + name, function(data) {
            window.data = data;
        });
    },

    setName: function(name) {
        // set a name value in the form
        this.$el.find('[name=firstname]').val(name);

        // trigger to set the URL hash
        this.trigger('name', name);

        // get stats
        this.getNameStats(name);
    }
});


