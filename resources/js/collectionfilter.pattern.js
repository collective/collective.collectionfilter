import { BasePattern } from "@patternslib/patternslib/src/core/basepattern";
import Parser from "@patternslib/patternslib/src/core/parser";
import registry from "@patternslib/patternslib/src/core/registry";
import Contentloader from "@plone/mockup/src/pat/contentloader/contentloader";

export const parser = new Parser("collectionfilter");
parser.addArgument("collectionUUID", null);
parser.addArgument("collectionURL", null);
parser.addArgument("reloadURL", null);
parser.addArgument("ajaxLoad", true);
parser.addArgument("contentSelector", "#content-core");

class Pattern extends BasePattern {
    static name = "collectionfilter";
    static trigger = ".pat-collectionfilter";
    static parser = parser;

    _initmap_cycles = 2;
    _zoomed = false;
    _ac = null;

    async init() {
        // Remove previous listeners if re-initialized
        if (this._ac) this._ac.abort();
        this._ac = new AbortController();
        const signal = this._ac.signal;

        this.el.addEventListener(
            "collectionfilter:reload",
            (e) => {
                const data = e.detail;
                if (
                    (data.noReloadSearch && this.el.classList.contains("collectionSearch")) ||
                    (data.noReloadMap && this.el.classList.contains("collectionMaps"))
                ) {
                    // don't reload search while typing or map while move/zooming
                    return;
                }
                if (data.collectionUUID === this.options.collectionUUID) {
                    this.reload(data.targetFilterURL);
                }
            },
            { signal }
        );

        // Collection Search
        if (this.el.classList.contains("collectionSearch") && this.options.ajaxLoad) {
            // initialize collection search

            this.el.querySelectorAll('button[type="submit"]').forEach((btn) => {
                btn.style.display = "none";
            });
            this.el.querySelectorAll("form").forEach((form) => {
                form.addEventListener("submit", (e) => e.preventDefault(), { signal });
            });
            let delayTimer;
            this.el.querySelectorAll('input[name="SearchableText"]').forEach((input) => {
                input.addEventListener(
                    "keyup",
                    (e) => {
                        clearTimeout(delayTimer);
                        // minimum 3 characters before searching
                        if (e.target.value.length > 0 && e.target.value.length < 3)
                            return;
                        delayTimer = setTimeout(() => {
                            let collectionURL = e.target.dataset.url;
                            const val = encodeURIComponent(e.target.value);
                            if (val) {
                                collectionURL += "&" + e.target.name + "=" + val;
                            }
                            this._dispatchReload({
                                collectionUUID: this.options.collectionUUID,
                                targetFilterURL: collectionURL,
                                noReloadSearch: true,
                            });
                            this.reloadCollection(collectionURL);
                        }, 500);
                    },
                    { signal }
                );
            });
            return; // no more action necessary.
        }

        // OPTION 1 - filter rendered as links
        // Do not handle click event for links with class ".collectionfilter-disabled"
        this.el
            .querySelectorAll(".filterContent a:not(.collectionfilter-disabled)")
            .forEach((a) => {
                a.addEventListener(
                    "click",
                    (e) => {
                        e.stopPropagation();
                        e.preventDefault();
                        // TODO: nextline: strange, it's not the anchor element itself,
                        // but a span. closest also catches the root element
                        // itself, so this shouldn't be a problem.
                        const collectionURL = e.target.closest("a").href;

                        this._dispatchReload({
                            collectionUUID: this.options.collectionUUID,
                            targetFilterURL: collectionURL,
                        });

                        this.reloadCollection(collectionURL);
                    },
                    { signal }
                );
            });

        // OPTION 2 - filter rendered as checkboxes or as pat-select2
        this.el.querySelectorAll(".filterContent input").forEach((input) => {
            input.addEventListener(
                "change",
                (e) => {
                    let collectionURL = null;

                    if (e.currentTarget.classList.contains("pat-select2")) {
                        // the pat-select2 field
                        const select2 = e.currentTarget;
                        const options = JSON.parse(select2.dataset.results);
                        let current_option = null;
                        if (e.added) {
                            // option is added
                            current_option = e.added;
                        } else {
                            // option is removed
                            current_option = e.removed;
                        }
                        const item = options.find((item) => item.title == current_option.text);
                        collectionURL = item.url;
                    } else {
                        // other checkboxes
                        collectionURL = e.target.dataset.url;
                    }

                    this._dispatchReload({
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL,
                    });

                    this.reloadCollection(collectionURL);
                },
                { signal }
            );
        });

        // OPTION 3 - filter rendered as dropdowns
        this.el.querySelectorAll(".filterContent select").forEach((select) => {
            select.addEventListener(
                "change",
                (e) => {
                    // See: https://stackoverflow.com/a/12750327/1337474
                    const option = e.target.selectedOptions[0];
                    const collectionURL = option.dataset.url;

                    this._dispatchReload({
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL,
                    });

                    this.reloadCollection(collectionURL);
                },
                { signal }
            );
        });

        // OPTION4 - maps filter
        if (this.el.classList.contains("collectionMaps")) {
            // Leaflet events are dispatched via jQuery - use lazy import
            const $ = (await import("jquery")).default;
            $(".pat-leaflet", this.el).on(
                "leaflet.moveend leaflet.zoomend",
                (e, le) => {
                    const narrow_down = e.target.dataset.narrowDownResult;
                    // do nothing if not narrowing down result
                    if (narrow_down.toLowerCase() === "false") return;

                    if (this._initmap_cycles > 0) {
                        // Do not trigger filter when initializing the map.
                        // One zoomend and one moveend events are thrown.
                        this._initmap_cycles -= 1;
                        return;
                    }

                    const levent = le["original_event"];
                    // prevent double loading when zooming (because it's always a move too)
                    if (levent.type === "moveend" && this._zoomed) {
                        this._zoomed = false;
                        return;
                    }
                    if (levent.type === "zoomend") this._zoomed = true;
                    let collectionURL = e.target.dataset.url;
                    const bounds = levent.target.getBounds();
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

                    this._dispatchReload({
                        collectionUUID: this.options.collectionUUID,
                        targetFilterURL: collectionURL,
                        noReloadMap: true,
                    });

                    this.reloadCollection(collectionURL);
                }
            );
        }
    }

    _dispatchReload(data) {
        document.querySelectorAll(this.trigger).forEach((el) => {
            el.dispatchEvent(
                new CustomEvent("collectionfilter:reload", {
                    bubbles: false,
                    detail: data,
                })
            );
        });
    }

    reload(filterURL) {
        if (!this.options.ajaxLoad) {
            window.location.href = filterURL;
            return;
        }
        const urlParts = this.options.reloadURL.split("?");
        const query1 = urlParts[1] || [];
        const query2 = filterURL.split("?")[1] || [];
        const query = [].concat(query1, query2).join("&");
        const reloadURL = [].concat(urlParts[0], query).join("?");

        new Contentloader(this.el, {
            url: reloadURL,
            target: this.el,
            content: "aside",
            trigger: "immediate",
        });
    }

    reloadCollection(collectionURL) {
        if (!this.options.ajaxLoad) return;
        new Contentloader(
            document.querySelector(this.options.contentSelector).parentElement, // let base element for setting classes and triggering events be the parent, which isn't replaced.
            {
                url: collectionURL + "&ajax_load=1",
                target: this.options.contentSelector,
                content: this.options.contentSelector,
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
        const re = /@@.*\//;
        collectionURL = collectionURL.replace(re, "");
        window.history.replaceState(
            {
                path: collectionURL,
            },
            "",
            collectionURL
        );
    }
}

registry.register(Pattern);
export default Pattern;
