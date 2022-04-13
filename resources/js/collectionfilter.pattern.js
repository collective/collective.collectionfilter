import Base from "@patternslib/patternslib/src/core/base";
import Parser from "@patternslib/patternslib/src/core/parser";
import Contentloader from "mockup/src/pat/contentloader/contentloader";

const parser = new Parser("collectionfilter");
parser.addArgument("collectionUUID", "");
parser.addArgument("collectionURL", "");
parser.addArgument("reloadURL", "");
parser.addArgument("ajaxLoad", true);
parser.addArgument("contentSelector", "#content-core");

export default Base.extend({
    name: "collectionfilter",
    trigger: ".pat-collectionfilter",
    _initmap_cycles: 2,
    _zoomed: false,

    init: function () {
        var self = this;

        self.options = parser.parse(self.$el, self.options);

        self.$el.unbind("collectionfilter:reload");

        self.$el.on("collectionfilter:reload", function (e, data) {
            if (
                (data.noReloadSearch && self.$el.hasClass("collectionSearch")) ||
                (data.noReloadMap && self.$el.hasClass("collectionMaps"))
            ) {
                // don't reload search while typing or map while move/zooming
                return;
            }
            if (data.collectionUUID === self.options.collectionUUID) {
                self.reload(data.targetFilterURL);
            }
        });

        // Collection Search
        if (self.$el.hasClass("collectionSearch") && self.options.ajaxLoad) {
            // initialize collection search

            $('button[type="submit"]', self.$el).hide();
            $("form", self.$el).on("submit", function (e) {
                e.preventDefault();
            });
            var delayTimer;
            $('input[name="SearchableText"]', self.$el).on("keyup", function (e) {
                clearTimeout(delayTimer);
                // minimum 3 characters before searching
                if ($(e.target).val().length > 0 && $(e.target).val().length < 3) return;
                delayTimer = setTimeout(function () {
                    var collectionURL = $(e.target).data("url");
                    var val = encodeURIComponent($(e.target).val());
                    if (val) {
                        collectionURL += "&" + $(e.target).attr("name") + "=" + val;
                    }
                    $(self.trigger).trigger("collectionfilter:reload", {
                        collectionUUID: self.options.collectionUUID,
                        targetFilterURL: collectionURL,
                        noReloadSearch: true,
                    });
                    self.reloadCollection(collectionURL);
                }, 500);
            });
            return; // no more action neccesarry.
        }

        // OPTION 1 - filter rendered as links
        $(".filterContent a", self.$el).on("click", function (e) {
            e.stopPropagation();
            e.preventDefault();
            // TODO: nextline: strange, it's not the anchor element itself,
            // but a span. jQuery's closest also catches the root element
            // itself, so this shouldn't be a problem.
            var collectionURL = $(e.target).closest("a").attr("href");

            $(self.trigger).trigger("collectionfilter:reload", {
                collectionUUID: self.options.collectionUUID,
                targetFilterURL: collectionURL,
            });

            self.reloadCollection(collectionURL);
        });

        // OPTION 2 - filter rendered as checkboxes
        $(".filterContent input", self.$el).on("change", function (e) {
            var collectionURL = $(e.target).data("url");

            self.$el.trigger("collectionfilter:reload", {
                collectionUUID: self.options.collectionUUID,
                targetFilterURL: collectionURL,
            });

            self.reloadCollection(collectionURL);
        });

        // OPTION 3 - filter rendered as dropdowns
        $(".filterContent select", self.$el).on("change", function (e) {
            // See: https://stackoverflow.com/a/12750327/1337474
            var option = $("option:selected", e.target);
            var collectionURL = $(option).data("url");

            $(self.trigger).trigger("collectionfilter:reload", {
                collectionUUID: self.options.collectionUUID,
                targetFilterURL: collectionURL,
            });

            self.reloadCollection(collectionURL);
        });

        // OPTION4 - maps filter
        if (self.$el.hasClass("collectionMaps")) {
            $(".pat-leaflet", self.$el).on(
                "leaflet.moveend leaflet.zoomend",
                function (e, le) {
                    var narrow_down = $(e.target).data("narrow-down-result");
                    // do nothing if not narrowing down result
                    if (narrow_down.toLowerCase() === "false") return;

                    if (self._initmap_cycles > 0) {
                        // Do not trigger filter when initializing the map.
                        // One zoomend and one moveend events are thrown.
                        self._initmap_cycles -= 1;
                        return;
                    }

                    var levent = le["original_event"];
                    // prevent double loading when zooming (because it's always a move too)
                    if (levent.type === "moveend" && self._zoomed) {
                        self._zoomed = false;
                        return;
                    }
                    if (levent.type === "zoomend") self._zoomed = true;
                    var collectionURL = $(e.target).data("url"),
                        bounds = levent.target.getBounds();
                    // generate bounds query
                    collectionURL +=
                        "&latitude.query:list:record=" +
                        bounds._northEast.lat +
                        "&latitude.query:list:record=" +
                        bounds._southWest.lat +
                        "&latitude.range:record=minmax";
                    collectionURL +=
                        "&longitude.query:list:record=" +
                        bounds._northEast.lng +
                        "&longitude.query:list:record=" +
                        bounds._southWest.lng +
                        "&longitude.range:record=minmax";

                    $(self.trigger).trigger("collectionfilter:reload", {
                        collectionUUID: self.options.collectionUUID,
                        targetFilterURL: collectionURL,
                        noReloadMap: true,
                    });

                    self.reloadCollection(collectionURL);
                }
            );
        }
    },

    reload: function (filterURL) {
        var self = this;
        if (!self.options.ajaxLoad) {
            window.location.href = filterURL;
            return;
        }
        var reloadURL = self.options.reloadURL;
        var urlParts = reloadURL.split("?");
        var query1 = urlParts[1] || [];
        var query2 = filterURL.split("?")[1] || [];
        var query = [].concat(query1, query2).join("&");
        reloadURL = [].concat(urlParts[0], query).join("?");

        new Contentloader(self.$el, {
            url: reloadURL,
            target: self.$el,
            content: "aside",
            trigger: "immediate",
        });
    },

    reloadCollection: function (collectionURL) {
        var self = this;

        if (!self.options.ajaxLoad) return;

        new Contentloader(
            $(self.options.contentSelector).parent(), // let base element for setting classes and triggering events be the parent, which isn't replaced.
            {
                url: collectionURL + "&ajax_load=1",
                target: self.options.contentSelector,
                content: self.options.contentSelector,
                trigger: "immediate",
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
        var re = /@@.*\//;
        collectionURL = collectionURL.replace(re, "");
        window.history.replaceState(
            {
                path: collectionURL,
            },
            "",
            collectionURL
        );
    },
});
