define([
    'jquery',
    'pat-base',
    'mockup-patterns-contentloader'
], function($, Base, contentloader) {

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
            this.$el.unbind('collectionfilter:reload');
            this.$el.on('collectionfilter:reload', function (e, data) {
                if (data.noReloadSearch && this.$el.hasClass('portletCollectionSearch')) {
                    // don't reload search portlet while typing.
                    return;
                }
                if (data.collectionUUID === this.options.collectionUUID) {
                    this.reload(data.targetFilterURL);
                }
            }.bind(this));

            // Collection Search
            if (this.$el.hasClass('portletCollectionSearch')) {
                // initialize collection search
                $('button[type="submit"]', this.$el).hide();
                $('form', this.$el).on('submit', function (e) {
                    e.preventDefault();
                });
                var delayTimer;
                $('input[name="SearchableText"]', this.$el).on('keyup', function (e) {
                    clearTimeout(delayTimer);
                    delayTimer = setTimeout(function() {
                        var collectionURL = $(e.target).data('url');
                        var val = encodeURIComponent($(e.target).val());
                        collectionURL += '&' + $(e.target).attr('name') + '=' + val;
                        $(this.trigger).trigger(
                            'collectionfilter:reload',
                            {
                                collectionUUID: this.options.collectionUUID,
                                targetFilterURL: collectionURL,
                                noReloadSearch: true
                            }
                        );
                        this.reloadCollection(collectionURL);
                    }.bind(this), 500);
                }.bind(this));
            }

            // OPTION 1 - filter rendered as links
            $('a.filteritem', this.$el).on('click', function (e) {
                e.stopPropagation();
                e.preventDefault();
                // TODO: nextline: strange, it's not the anchor element itself,
                // but a span. jQuery's closest also catches the root element
                // itself, so this shouldn't be a problem.
                var collectionURL = $(e.target).closest('a').attr('href');

                $(this.trigger).trigger(
                    'collectionfilter:reload',
                    {
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL
                    }
                );

                this.reloadCollection(collectionURL);
            }.bind(this));

            // OPTION 2 - filter rendered as checkboxes
            $('input.filteritem', this.$el).on('change', function (e) {
                var collectionURL = $(e.target).data('url');

                $(this.trigger).trigger(
                    'collectionfilter:reload',
                    {
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL
                    }
                );

                this.reloadCollection(collectionURL);
            }.bind(this));

            // OPTION 3 - filter rendered as dropdowns
            $('select.filteritem', this.$el).on('change', function (e) {
                // See: https://stackoverflow.com/a/12750327/1337474
                var option = $('option:selected', e.target);
                var collectionURL = $(option).data('url');

                $(this.trigger).trigger(
                    'collectionfilter:reload',
                    {
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL
                    }
                );

                this.reloadCollection(collectionURL);
            }.bind(this));

        },

        reload: function (filterURL) {

            var reloadURL = this.options.reloadURL;
            var urlParts = reloadURL.split('?');
            var query1 = urlParts[1] || [];
            var query2 = filterURL.split('?')[1] || [];
            var query = [].concat(query1, query2).join('&');
            reloadURL = [].concat(urlParts[0], query).join('?');

            var cl = new this.contentloader(this.$el, {
                url: reloadURL,
                target: this.$el,
                content: 'aside',
                trigger: 'immediate'
            });
        },

        reloadCollection: function (collectionURL) {
            var cl = new this.contentloader(this.$el, {
                url: collectionURL + '&ajax_load=1',
                target: '#content-core',
                content: '#content-core',
                trigger: 'immediate'
            });
            // TODO: remove this, once ``contentloader`` handles history
            // updates itself and adds ajax_load.
            window.history.replaceState(
                {path: collectionURL},
                '',
                collectionURL
            );
        }

    });

    return CollectionFilter;
});
