define([
    'jquery',
    'pat-base',
    'mockup-patterns-contentloader'
], function ($, Base, contentloader) {

    var CollectionFilter = Base.extend({
        name: 'collectionfilter',
        trigger: '.pat-collectionfilter',
        parser: 'mockup',
        contentloader: contentloader,
        defaults: {
            collectionUUID: '',
            collectionURL: '',
            reloadURL: '',
            ajaxLoad: true,
            contentSelector: '#content-core',
        },
        _initmap_cycles: 2,
        _zoomed: false,

        init: function () {
            this.$el.unbind('collectionfilter:reload');
            this.$el.on('collectionfilter:reload', function (e, data) {
                if ((data.noReloadSearch && this.$el.hasClass('collectionSearch')) ||
                    (data.noReloadMap && this.$el.hasClass('collectionMaps'))) {
                    // don't reload search while typing or map while move/zooming
                    return;
                }
                if (data.collectionUUID === this.options.collectionUUID) {
                    this.reload(data.targetFilterURL);
                }
            }.bind(this));

            // Collection Search
            if (this.$el.hasClass('collectionSearch') && this.options.ajaxLoad) {
                // initialize collection search

                $('button[type="submit"]', this.$el).hide();
                $('form', this.$el).on('submit', function (e) {
                    e.preventDefault();
                });
                var delayTimer;
                $('input[name="SearchableText"]', this.$el).on('keyup', function (e) {
                    clearTimeout(delayTimer);
                    // minimum 3 characters before searching
                    if (($(e.target).val().length > 0) && ($(e.target).val().length < 3)) return;
                    delayTimer = setTimeout(function () {
                        var collectionURL = $(e.target).data('url');
                        var val = encodeURIComponent($(e.target).val());
                        if (val) {
                            collectionURL += '&' + $(e.target).attr('name') + '=' + val;
                        }
                        $(this.trigger).trigger(
                            'collectionfilter:reload', {
                                collectionUUID: this.options.collectionUUID,
                                targetFilterURL: collectionURL,
                                noReloadSearch: true
                            }
                        );
                        this.reloadCollection(collectionURL);
                    }.bind(this), 500);
                }.bind(this));
                return; // no more action neccesarry.
            }

            // OPTION 1 - filter rendered as links
            $('.filterContent a', this.$el).on('click', function (e) {
                e.stopPropagation();
                e.preventDefault();
                // TODO: nextline: strange, it's not the anchor element itself,
                // but a span. jQuery's closest also catches the root element
                // itself, so this shouldn't be a problem.
                var collectionURL = $(e.target).closest('a').attr('href');

                $(this.trigger).trigger(
                    'collectionfilter:reload', {
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL
                    }
                );

                this.reloadCollection(collectionURL);
            }.bind(this));

            // OPTION 2 - filter rendered as checkboxes
            $('.filterContent input', this.$el).on('change', function (e) {
                var collectionURL = $(e.target).data('url');

                $(this.trigger).trigger(
                    'collectionfilter:reload', {
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL
                    }
                );

                this.reloadCollection(collectionURL);
            }.bind(this));

            // OPTION 3 - filter rendered as dropdowns
            $('.filterContent select', this.$el).on('change', function (e) {
                // See: https://stackoverflow.com/a/12750327/1337474
                var option = $('option:selected', e.target);
                var collectionURL = $(option).data('url');

                $(this.trigger).trigger(
                    'collectionfilter:reload', {
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL
                    }
                );

                this.reloadCollection(collectionURL);
            }.bind(this));

            // OPTION4 - maps filter
            if (this.$el.hasClass('collectionMaps')) {
                $('.pat-leaflet', this.$el).on('leaflet.moveend leaflet.zoomend', function (e, le) {
                    var narrow_down = $(e.target).data('narrow-down-result');
                    // do nothing if not narrowing down result
                    if (narrow_down.toLowerCase() === 'false') return;

                    if (this._initmap_cycles > 0) {
                        // Do not trigger filter when initializing the map.
                        // One zoomend and one moveend events are thrown.
                        this._initmap_cycles -= 1;
                        return;
                    }

                    var levent = le['original_event'];
                    // prevent double loading when zooming (because it's always a move too)
                    if (levent.type === 'moveend' && this._zoomed) {
                        this._zoomed = false;
                        return
                    }
                    if (levent.type === 'zoomend') this._zoomed = true;
                    var collectionURL = $(e.target).data('url'),
                        bounds = levent.target.getBounds();
                    // generate bounds query
                    collectionURL += "&latitude.query:list:record=" + bounds._northEast.lat + "&latitude.query:list:record=" + bounds._southWest.lat + "&latitude.range:record=minmax";
                    collectionURL += "&longitude.query:list:record=" + bounds._northEast.lng + "&longitude.query:list:record=" + bounds._southWest.lng + "&longitude.range:record=minmax";

                    $(this.trigger).trigger(
                        'collectionfilter:reload', {
                            collectionUUID: this.options.collectionUUID,
                            targetFilterURL: collectionURL,
                            noReloadMap: true
                        }
                    );

                    this.reloadCollection(collectionURL);
                }.bind(this));

                $(".pat-leaflet", this.$el).on("leaflet.geojson.load", function(e) {
                    $(".plone-loader", this.$el).show();
                }.bind(this));

                $(".pat-leaflet", this.$el).on("leaflet.geojson.loaded", function(e, data) {
                    $(".plone-loader", this.$el).hide();
                }.bind(this));
            }
        },

        reload: function (filterURL) {
            if (!this.options.ajaxLoad) {
                window.location.href = filterURL;
                return
            }
            var reloadURL = this.options.reloadURL;
            var urlParts = reloadURL.split('?');
            var query1 = urlParts[1] || [];
            var query2 = filterURL.split('?')[1] || [];
            var query = [].concat(query1, query2).join('&');
            reloadURL = [].concat(urlParts[0], query).join('?');
            var cl = new this.contentloader(
                this.$el, {
                    url: reloadURL,
                    target: this.$el,
                    content: 'aside',
                    trigger: 'immediate'
                }
            );
        },

        reloadCollection: function (collectionURL) {
            if (!this.options.ajaxLoad)
                return;
            var cl = new this.contentloader(
                $(this.options.contentSelector).parent(), // let base element for setting classes and triggering events be the parent, which isn't replaced.
                {
                    url: collectionURL + '&ajax_load=1',
                    target: this.options.contentSelector,
                    content: this.options.contentSelector,
                    trigger: 'immediate'
                }
            );
            // TODO: remove this, once ``contentloader`` handles history
            // updates itself and adds ajax_load.
            //
            // Search for all @@ views in ajax calls and remove it before
            // adding it to the browser history
            //
            // XXX: This leads to unwanted browser url when the context
            // is not the collection for eg. a Mosaic Page with filter
            // tiles.
            re = /@@.*\//;
            collectionURL = collectionURL.replace(re, '');
            window.history.replaceState({
                    path: collectionURL
                },
                '',
                collectionURL
            );
        }

    });

    return CollectionFilter;
});