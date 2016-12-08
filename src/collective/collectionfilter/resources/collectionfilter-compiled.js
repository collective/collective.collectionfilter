define("mockup-patterns-contentloader",["jquery","pat-base","pat-logger","pat-registry","mockup-utils","underscore"],function(a,b,c,d,e,f){"use strict";var g=c.getLogger("pat-contentloader"),h=b.extend({name:"contentloader",trigger:".pat-contentloader",parser:"mockup",defaults:{url:null,content:null,trigger:"click",target:null,template:null,dataType:"html"},init:function(){var a=this;"el"===a.options.url&&"A"===a.$el[0].tagName&&(a.options.url=a.$el.attr("href")),"immediate"===a.options.trigger?a._load():a.$el.on(a.options.trigger,function(b){b.preventDefault(),a._load()})},_load:function(){var a=this;a.$el.addClass("loading-content"),a.options.url?a.loadRemote():a.loadLocal()},loadRemote:function(){var b=this;a.ajax({url:b.options.url,dataType:b.options.dataType,success:function(c){var d;if("html"===b.options.dataType)c.indexOf("<html")!==-1&&(c=e.parseBodyTag(c)),d=a("<div>"+c+"</div>");else if(b.options.dataType.indexOf("json")!==-1){c.constructor===Array&&1===c.length&&(c=c[0]);try{d=a(f.template(b.options.template)(c))}catch(h){return void g.warn("error rendering template. pat-contentloader will not work")}}null!==b.options.content&&(d=d.find(b.options.content)),b.loadLocal(d),b.$el.removeClass("loading-content")},error:function(){b.$el.addClass("content-load-error")}})},loadLocal:function(b){var c=this;if(!b&&null===c.options.content)return void g.warn("No selector configured");var e=c.$el;return null!==c.options.target&&(e=a(c.options.target),0===e.size())?void g.warn("No target nodes found"):(b||(b=a(c.options.content).clone()),b.show(),e.replaceWith(b),d.scan(b),void c.$el.removeClass("loading-content"))}});return h}),define("collectionfilter",["jquery","pat-base","mockup-patterns-contentloader"],function(a,b,c){"use strict";var d=b.extend({name:"collectionfilter",trigger:".pat-collectionfilter",parser:"mockup",contentloader:c,defaults:{collectionUUID:"",collectionURL:"",reloadURL:""},init:function(){this.options.additive&&(this.$el.unbind("collectionfilter:reload"),this.$el.on("collectionfilter:reload",function(a,b){b.collectionUUID===this.options.collectionUUID&&this.reload(b.targetFilterURL)}.bind(this))),a(".filteritem",this.$el).on("click",function(b){b.stopPropagation(),b.preventDefault();var c=b.target.closest("a").href;this.options.additive&&a(this.trigger).trigger("collectionfilter:reload",{collectionUUID:this.options.collectionUUID,targetFilterURL:c}),this.reloadCollection(c+"&ajax_load=1")}.bind(this))},reload:function(a){var b=this.options.reloadURL;if(this.options.additive)var c=b.split("?"),d=c[1]||[],e=a.split("?")[1]||[],f=[].concat(d,e).join("&"),b=[].concat(c[0],f).join("?");new this.contentloader(this.$el,{url:b,target:this.$el,content:"aside",trigger:"immediate"})},reloadCollection:function(a){new this.contentloader(this.$el,{url:a,target:"#content-core",content:"#content-core",trigger:"immediate"})}});return d}),require(["jquery","pat-registry","collectionfilter"],function(a,b){"use strict";window.parent===window&&a(document).ready(function(){b.initialized||b.init()})}),define("/home/_thet/data/dev/agitator/collectionfilter/plone/src/collective.collectionfilter/src/collective/collectionfilter/resources/collectionfilter-bundle.js",function(){});
//# sourceMappingURL=collectionfilter-compiled.js.map