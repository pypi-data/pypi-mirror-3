Hilite={elementid:"content",exact:true,max_nodes:1000,onload:true,style_name:"hilite",style_name_suffix:true,debug_referrer:""};Hilite.search_engines=[["google\\.","q"],["search\\.yahoo\\.","p"],["search\\.msn\\.","q"],["search\\.live\\.","query"],["search\\.aol\\.","userQuery"],["ask\\.com","q"],["altavista\\.","q"],["feedster\\.","q"],["search\\.lycos\\.","q"],["alltheweb\\.","q"],["technorati\\.com/search/([^\\?/]+)",1],["dogpile\\.com/info\\.dogpl/search/web/([^\\?/]+)",1,true]];Hilite.decodeReferrer=function(d){var g=null;var e=new RegExp("");for(var c=0;c<Hilite.search_engines.length;c++){var f=Hilite.search_engines[c];e.compile("^http://(www\\.)?"+f[0],"i");var b=d.match(e);if(b){var a;if(isNaN(f[1])){a=Hilite.decodeReferrerQS(d,f[1])}else{a=b[f[1]+1]}if(a){a=decodeURIComponent(a);if(f.length>2&&f[2]){a=decodeURIComponent(a)}a=a.replace(/\'|"/g,"");a=a.split(/[\s,\+\.]+/);return a}break}}return null};Hilite.decodeReferrerQS=function(f,d){var b=f.indexOf("?");var c;if(b>=0){var a=new String(f.substring(b+1));b=0;c=0;while((b>=0)&&((c=a.indexOf("=",b))>=0)){var e,g;e=a.substring(b,c);b=a.indexOf("&",c)+1;if(e==d){if(b<=0){return a.substring(c+1)}else{return a.substring(c+1,b-1)}}else{if(b<=0){return null}}}}return null};Hilite.hiliteElement=function(f,e){if(!e||f.childNodes.length==0){return}var c=new Array();for(var b=0;b<e.length;b++){e[b]=e[b].toLowerCase();if(Hilite.exact){c.push("\\b"+e[b]+"\\b")}else{c.push(e[b])}}c=new RegExp(c.join("|"),"i");var a={};for(var b=0;b<e.length;b++){if(Hilite.style_name_suffix){a[e[b]]=Hilite.style_name+(b+1)}else{a[e[b]]=Hilite.style_name}}var d=function(m){var j=c.exec(m.data);if(j){var n=j[0];var i="";var h=m.splitText(j.index);var g=h.splitText(n.length);var l=m.ownerDocument.createElement("SPAN");m.parentNode.replaceChild(l,h);l.className=a[n.toLowerCase()];l.appendChild(h);return l}else{return m}};Hilite.walkElements(f.childNodes[0],1,d)};Hilite.hilite=function(){var a=Hilite.debug_referrer?Hilite.debug_referrer:document.referrer;var b=null;a=Hilite.decodeReferrer(a);if(a&&((Hilite.elementid&&(b=document.getElementById(Hilite.elementid)))||(b=document.body))){Hilite.hiliteElement(b,a)}};Hilite.walkElements=function(d,f,e){var a=/^(script|style|textarea)/i;var c=0;while(d&&f>0){c++;if(c>=Hilite.max_nodes){var b=function(){Hilite.walkElements(d,f,e)};setTimeout(b,50);return}if(d.nodeType==1){if(!a.test(d.tagName)&&d.childNodes.length>0){d=d.childNodes[0];f++;continue}}else{if(d.nodeType==3){d=e(d)}}if(d.nextSibling){d=d.nextSibling}else{while(f>0){d=d.parentNode;f--;if(d.nextSibling){d=d.nextSibling;break}}}}};if(Hilite.onload){if(window.attachEvent){window.attachEvent("onload",Hilite.hilite)}else{if(window.addEventListener){window.addEventListener("load",Hilite.hilite,false)}else{var __onload=window.onload;window.onload=function(){Hilite.hilite();__onload()}}}};