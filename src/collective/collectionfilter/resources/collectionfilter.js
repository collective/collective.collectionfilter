define([
    'jquery',
    'pat-base',
    'mockup-patterns-contentloader'
], function($, Base, contentloader) {

    'use strict';

    var CollectionFilter = Base.extend({
        name: 'collectionfilter',
        trigger: '.pat-collectionfilter',
        parser: 'mockup',
        contentloader: contentloader,
        defaults: {
            collectionUUID: '',
            collectionURL: '',
            reloadURL: ''
        },

        init: function() {
            $(document).on('collectionfilter:reload', function (e, data) {
                if (data.collectionUUID === this.options.collectionUUID) {
                    this.reload();
                }
            }.bind(this));
            $('.filteritem', this.$el).on('click', function (e) {
                e.stopPropagation();
                e.preventDefault();
                $(document).trigger(
                    'collectionfilter:reload',
                    {collectionUUID: this.options.collectionUUID}
                );

                var url = e.target.closest('a').href  // dunno why, but e.target here is a span el, when it should be the a tag. this fixes it forward/backwards compatible...
                this.reloadCollection(url + '&ajax_load=1');
            }.bind(this));
        },

        reload: function () {
            var cl = new this.contentloader(this.$el, {
                url: this.options.reloadURL,
                target: this.$el,
                trigger: 'immediate'
            });
        },

        reloadCollection: function (url) {
            var cl = new this.contentloader(this.$el, {
                url: url,
                target: '#content-core',
                content: '#content-core',
                trigger: 'immediate'
            });
        }

    });

    return CollectionFilter;
});
