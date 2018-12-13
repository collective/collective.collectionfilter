define("collectionfilter",["jquery","pat-base","mockup-patterns-contentloader"],function(a,b,c){var d=b.extend({name:"collectionfilter",trigger:".pat-collectionfilter",parser:"mockup",contentloader:c,defaults:{collectionUUID:"",collectionURL:"",reloadURL:"",contentSelector:"#content-core"},init:function(){if(console.log("filter init start"),this.$el.unbind("collectionfilter:reload"),this.$el.on("collectionfilter:reload",function(a,b){b.noReloadSearch&&this.$el.hasClass("collectionSearch")||b.collectionUUID===this.options.collectionUUID&&this.reload(b.targetFilterURL)}.bind(this)),this.$el.hasClass("collectionSearch")){console.log("filter search init start"),a('button[type="submit"]',this.$el).hide(),a("form",this.$el).on("submit",function(a){a.preventDefault()});var b;return void a('input[name="SearchableText"]',this.$el).on("keyup",function(c){clearTimeout(b),b=setTimeout(function(){var b=a(c.target).data("url"),d=encodeURIComponent(a(c.target).val());b+="&"+a(c.target).attr("name")+"="+d,a(this.trigger).trigger("collectionfilter:reload",{collectionUUID:this.options.collectionUUID,targetFilterURL:b,noReloadSearch:!0}),this.reloadCollection(b)}.bind(this),500)}.bind(this))}a(".filterContent a",this.$el).on("click",function(b){b.stopPropagation(),b.preventDefault();var c=a(b.target).closest("a").attr("href");a(this.trigger).trigger("collectionfilter:reload",{collectionUUID:this.options.collectionUUID,targetFilterURL:c}),this.reloadCollection(c)}.bind(this)),a(".filterContent input",this.$el).on("change",function(b){var c=a(b.target).data("url");a(this.trigger).trigger("collectionfilter:reload",{collectionUUID:this.options.collectionUUID,targetFilterURL:c}),this.reloadCollection(c)}.bind(this)),a(".filterContent select",this.$el).on("change",function(b){var c=a("option:selected",b.target),d=a(c).data("url");a(this.trigger).trigger("collectionfilter:reload",{collectionUUID:this.options.collectionUUID,targetFilterURL:d}),this.reloadCollection(d)}.bind(this)),console.log("filter init end bind")},reload:function(a){var b=this.options.reloadURL,c=b.split("?"),d=c[1]||[],e=a.split("?")[1]||[],f=[].concat(d,e).join("&");b=[].concat(c[0],f).join("?");new this.contentloader(this.$el,{url:b,target:this.$el,content:"aside",trigger:"immediate"})},reloadCollection:function(b){new this.contentloader(a(this.options.contentSelector).parent(),{url:b+"&ajax_load=1",target:this.options.contentSelector,content:this.options.contentSelector,trigger:"immediate"});re=/@@.*\//,b=b.replace(re,""),window.history.replaceState({path:b},"",b),console.log("filter search init start")}});return d}),require(["jquery","pat-registry","collectionfilter"],function(a,b){"use strict"});
//# sourceMappingURL=collectionfilter-bundle-compiled.js.map