jQuery.JSON = {
useHasOwn : ({}.hasOwnProperty ? true : false),
pad : function(n) {
return n < 10 ? "0" + n : n;
},
m : {
"\b": '\\b',
"\t": '\\t',
"\n": '\\n',
"\f": '\\f',
"\r": '\\r',
'"' : '\\"',
"\\": '\\\\'
},
encodeString : function(s){
if (/["\\\x00-\x1f]/.test(s)) {
return '"' + s.replace(/([\x00-\x1f\\"])/g, function(a, b) {
var c = m[b];
if(c){
return c;
}
c = b.charCodeAt();
return "\\u00" +
Math.floor(c / 16).toString(16) +
(c % 16).toString(16);
}) + '"';
}
return '"' + s + '"';
},
encodeArray : function(o){
var a = ["["], b, i, l = o.length, v;
for (i = 0; i < l; i += 1) {
v = o[i];
switch (typeof v) {
case "undefined":
case "function":
case "unknown":
break;
default:
if (b) {
a.push(',');
}
a.push(v === null ? "null" : this.encode(v));
b = true;
}
}
a.push("]");
return a.join("");
},
encodeDate : function(o){
return '"' + o.getFullYear() + "-" +
pad(o.getMonth() + 1) + "-" +
pad(o.getDate()) + "T" +
pad(o.getHours()) + ":" +
pad(o.getMinutes()) + ":" +
pad(o.getSeconds()) + '"';
},
encode : function(o){
if(typeof o == "undefined" || o === null){
return "null";
}else if(o instanceof Array){
return this.encodeArray(o);
}else if(o instanceof Date){
return this.encodeDate(o);
}else if(typeof o == "string"){
return this.encodeString(o);
}else if(typeof o == "number"){
return isFinite(o) ? String(o) : "null";
}else if(typeof o == "boolean"){
return String(o);
}else {
var self = this;
var a = ["{"], b, i, v;
for (i in o) {
if(!this.useHasOwn || o.hasOwnProperty(i)) {
v = o[i];
switch (typeof v) {
case "undefined":
case "function":
case "unknown":
break;
default:
if(b){
a.push(',');
}
a.push(self.encode(i), ":",
v === null ? "null" : self.encode(v));
b = true;
}
}
}
a.push("}");
return a.join("");
}
},
decode : function(json){
return eval("(" + json + ')');
}
};

// The console object
var console_object = {
	log: function () {},
	debug: function () {},
	info: function () {},
	warn: function () {},
	error: function () {},
	assert: function () {},
	dir: function () {},
	dirxml: function () {},
	trace: function () {},
	group: function () {},
	groupCollapsed: function () {},
	groupEnd: function () {},
	time: function () {},
	timeEnd: function () {},
	profile: function () {},
	count: function () {}
};

// Simulate Firebug console-functions if they don't exist
if (typeof(console) === "undefined") {
	// JSLint throws a redefinition error on this, but we can ignore it,
	// because we check if console undefined before defining it and
	// we remove the whole console stuff on a non development build
	var console = {};
}
// merge the console_object with the current console object
// we do this because some browsers support only console.log but some other functions are missing
var obj_name;
for (obj_name in console_object) {
	if (typeof(obj_name) === "string" && console[obj_name] === undefined) {
		console[obj_name] = console_object[obj_name];
	}
}

var TuVedi = {
	presentation: {
		template: {
			"id": null,
			"class": ""
		},
		areas: {}
	},
	presentation_load: undefined,
	presentation_lock: false,
	areas_updated: {},
	areas_timestamp: {},
	presentation_updated: 0,
	component_ids: [],
	widgets2load: [],
	widgets2load_count: 0,
	widgets2remove: {},
	session_id: 0,
	new_class: undefined,
	tmp_template: undefined,
	tmp_style: undefined,
	check: function() {
		// check if the update function is working		
	},
	start: function(options) {
		//TuVedi.options = $.extend(TuVedi.options, options);
		TuVedi.Config.update(options);
		setInterval("TuVedi.check()", 60000);
		TuVedi.Resource.onReady(function() {
			TuVedi.update();
		});
	},
	add_widget: function(area_name, area) {
		TuVedi.widgets2load_count++;
		TuVedi.presentation['areas'][area_name] = area;
		//
		if(area["type"] === "url") {
			//
			if (area["target"] == "iframe") {
				//
				var content = $(TuVedi.tmp_template).find("#"+area_name).find(".content");
				content.hide();
				content.removeClass("content").addClass("loading");

				content.html('<iframe src="'+area['prefs']['url']+'" height="100%" width="100%" frameborder="0"></iframe>');
				$("#"+area_name).find(".content").parent().append(content);
				//
				var session_id = TuVedi.session_id;
				content.find("iframe").load(function(a) {TuVedi.widget_ready(area_name, session_id);})
			} else if(area["target"] == "intern") {
				var content = $(TuVedi.tmp_template).find("#"+area_name).find(".content");
				content.hide();
				content.removeClass("content").addClass("loading");
				jQuery.ajax({
					url: area['prefs']['url'],
					dataType: "html",
					//crossDomain: true,
					success: function(data) {
						content.html(data);
						$("#"+area_name).find(".content").parent().append(content);
						var session_id = TuVedi.session_id;
						TuVedi.widget_ready(area_name, session_id);
					}
				});
			}
		} else if(area['type'] === "jquery") {
			//
			var content = $(TuVedi.tmp_template).find("#"+area_name).find(".content");
			content.hide();
			content.removeClass("content").addClass("loading");

			$("#"+area_name).find(".content").parent().append(content);
			var node = $("#"+area_name).find(".loading");
			$.fn[area['js_name']].call(node, area['prefs'], TuVedi.widget_ready, area_name, TuVedi.session_id);
		}
	},
	start_session: function() {
		TuVedi.session_id = new Date().getTime();
	},
	widget_ready: function(area_name, session_id) {
		if(TuVedi.session_id === session_id) {
			TuVedi.widgets2load_count--;
			TuVedi.widgets2load.push(area_name);
		}
	},
	show_widget: function(force) {
		//
		var area;
		if(TuVedi.widgets2load_count === 0 && TuVedi.presentation_lock === false || force === true) {
			TuVedi.session_id = 0;
			var area_name;
			if(TuVedi.new_class !== TuVedi.presentation["template"]["class"] && TuVedi.new_class !== undefined) {
				var areas_not_changed = {};
				var area_element;

				for(area_name in TuVedi.presentation['areas']) {
					if(TuVedi.presentation['areas'][area_name] !== null && jQuery.inArray(area_name, TuVedi.widgets2load) === -1 && TuVedi.widgets2remove[area_name] === undefined) {
						if(TuVedi.presentation['areas'][area_name]['type'] === "jquery") {
							area_element = $("#"+area_name).find(".content");
							areas_not_changed[area_name] = {
								width: area_element.width(),
								height: area_element.height(),
								element: area_element
							};
						}
					}
				}
				$(document.body).removeClass().addClass(TuVedi.new_class);
				TuVedi.presentation["template"]["class"] = TuVedi.new_class;
				for(area_name in areas_not_changed) {
					area = areas_not_changed[area_name];
					if(area['width'] !== area['element'].width() || area['height'] !== area['element'].height()) {
						$.fn[TuVedi.presentation['areas'][area_name]['js_name']].call($("#"+area_name).find(".content"), "resize");
					}
				}
			}
			for(i = 0; i < TuVedi.widgets2load.length; i++) {
				area_name = TuVedi.widgets2load[i];
				area = area = TuVedi.presentation['areas'][area_name];
				$("#"+area_name).find(".content").toggleClass("remove content").hide();
				$("#"+area_name).find(".loading").toggleClass("loading content").show();
				$("#"+area_name).show();
				if(area['type'] === "jquery") {
					$.fn[area['js_name']].call($("#"+area_name).find(".content"), "show");
				}
			}
			for(i = 0; i < TuVedi.widgets2load.length; i++) {
				area_name = TuVedi.widgets2load[i];
				if(TuVedi.widgets2remove[area_name] !== undefined) {
					var node_remove = $("#"+area_name).find(".remove");
					TuVedi.destroy_widget(area_name, TuVedi.widgets2remove[area_name], node_remove);
					node_remove.remove();
				}
				TuVedi.widgets2remove[area_name] = undefined;
			}
			$(".remove").remove();
			TuVedi.widgets2load = [];
			TuVedi.widgets2load_count = 0;
			for(area_name in TuVedi.widgets2remove) {
				var area = TuVedi.widgets2remove[area_name];
				if (area !== undefined && area !== null) {
					$("#" + area_name).hide();
					TuVedi.destroy_widget(area_name, area, $("#"+area_name).find(".content"));
					TuVedi.presentation['areas'][area_name] = null;
				}
			}
			TuVedi.widgets2remove = {};
		} else {
			setTimeout("TuVedi.show_widget()", 1000);
		}
	},
	destroy_widget: function(area_name, area, node) {
		if(area['type'] === "url") {
			if (area["target"] === "iframe" || area["target"] === "intern") {
				node.empty();
			}
		} else if(area['type'] === "jquery") {
			$.fn[area['js_name']].call(node, 'destroy');
			node.empty();
		}
	},
	remove_widget: function(area_name, area) {
		TuVedi.widgets2remove[area_name] = area;
	},
	update_widget: function(area_name, area) {
		TuVedi.presentation['areas'][area_name]['last_modified'] = area['last_modified'];
		TuVedi.presentation['areas'][area_name]['prefs'] = area['prefs'];
		if(area['type'] === "url") {
			if (area["target"] === "iframe") {
				$("#"+area_name).find(".content").find("iframe").attr("src", area['prefs']['url']);
			} else if (area["target"] === "intern") {
				jQuery.ajax({
					url: area['prefs']['url'],
					dataType: "html",
					success: function(data) {
						$("#"+area_name).find(".content").html(data);
					}
				});
				$("#"+area_name).find(".content").empty();
			}
		} else if(area['type'] === "jquery") {
			$.fn[area['js_name']].call($("#"+area_name).find(".content"), 'update', area['prefs']);
			$("#" + area_name).show();
		}
	},
	update: function() {
		function copy_attributes(obj) {
			var obj_new = {};
			var i;
			for(i=0; i < arguments.length; i++) {
				obj_new[arguments[i]] = obj[arguments[i]];
			}
			return obj_new;
		}
		var current_presentation = {
			template: copy_attributes(TuVedi.presentation['template'], "id", "class"),
			areas: {}
		}
		var areas = TuVedi.presentation['areas'];
		if(areas !== undefined) {
			var name;
			for(name in areas) {
				if(areas[name] !== null) {
					current_presentation['areas'][name] = copy_attributes(
						areas[name],
						"widget_id",
						"last_modified"
					);
				}
			}
		}
		jQuery.ajax({
			url: TuVedi.URL.joinTuVedi("update", TuVedi.Config.get('device')),
			dataType: "json",
			type: "POST",
			data: {
				data: $.JSON.encode(current_presentation)
			},
			//crossDomain: true,
			success: function(data) {
				//
				// change the template
				TuVedi.show_widget(true);
				var cmp_id, i;
				if(TuVedi.presentation_load !== undefined) {
					// we are currently loading a template, so stop here
					return;
				}
				for(i = 0; i < data['component_ids'].length; i++) {
					cmp_id = data['component_ids'][i];
					if(jQuery.inArray(cmp_id, TuVedi.component_ids) === -1) {
						TuVedi.component_ids.push(cmp_id);
						TuVedi.Resource.loadScript(TuVedi.URL.joinTuVedi("get-component", cmp_id));
					}
				}
				// wait until all components are loaded
				TuVedi.Resource.onReady(function () {
					// wait until all requirements are loaded
					TuVedi.Resource.onReady(function () {
						if(data["template"]["id"] !== TuVedi.presentation["template"]["id"]) {
							TuVedi.presentation_load = data;
							jQuery.ajax({
								url: TuVedi.URL.joinTuVedi("get-template", TuVedi.presentation_load["template"]["id"]),
								dataType: "html",
								success: function(data) {
									TuVedi.tmp_template = data;
									jQuery.ajax({
										url: TuVedi.URL.joinTuVedi("get-style", TuVedi.presentation_load["template"]["id"]),
										dataType: "text",
										success: function(data) {
											TuVedi.tmp_style = data;
											//
											// replace body content
											$(document.body).empty();
											// remove all css classes from body
											$(document.body).removeClass();
											$("head").find("style").empty();
											// add new style
											// add hide option to all areas
											for(area_name in TuVedi.presentation_load['areas']) {
												data = data + "\n#"+area_name + "{display:none}\n";
											}
											$("head").append('<style type="text/css">' + data + '</style>');

											$(document.body).append(TuVedi.tmp_template);
											$(document.body).addClass(TuVedi.presentation_load["template"]["class"]);
											var area;
											TuVedi.start_session();
											for(area_name in TuVedi.presentation_load['areas']) {
												area = TuVedi.presentation_load['areas'][area_name];
												if(area !== null) {
													TuVedi.add_widget(area_name, area);
													//$("#" + area_name).show();
												}
											}
											TuVedi.presentation["areas"] = TuVedi.presentation_load["areas"];
											TuVedi.presentation["template"]["id"] = TuVedi.presentation_load["template"]["id"];
											TuVedi.presentation["template"]["class"] = TuVedi.presentation_load["template"]["class"];
											TuVedi.presentation_load = undefined;
											TuVedi.show_widget();
										}
									});
								}
							});
						} else if(data["template"]["class"] !== TuVedi.presentation["template"]["class"]) {
							TuVedi.new_class = data["template"]["class"];
						}
						var area;
						var area_cur;
						TuVedi.presentation_lock = true;
						TuVedi.start_session();
						for(area_name in data['areas']) {
							area = data['areas'][area_name];
							area_cur = TuVedi.presentation['areas'][area_name];

							if(area === null) {
								// remove the widget
								TuVedi.remove_widget(area_name, TuVedi.presentation['areas'][area_name]);
							} else if(area_cur !== undefined && TuVedi.presentation['areas'][area_name] === null) {
								// add a widget
								TuVedi.add_widget(area_name, area);
							} else if(area_cur !== undefined && area['widget_id'] !== TuVedi.presentation['areas'][area_name]['widget_id']) {
								// replace a widget with a new one
								TuVedi.remove_widget(area_name, TuVedi.presentation[area_name]);
								TuVedi.add_widget(area_name, area);
							} else if(area_cur !== undefined && area['modified'] === true) {
								// update the widget configuration
								TuVedi.update_widget(area_name, area);
							}
						}
						TuVedi.presentation_lock = false;
						TuVedi.show_widget();
					});
				});
			}
		})
		setTimeout("TuVedi.update()", TuVedi.Config.get('refresh'));
	}
};
/**
This class handles all our config stuff. Use it to get values for the different config options.

@class TuVedi.Config
*/

(function () {
	TuVedi.Config = {
		/**
		@var {private Array} config key => value list with all config options
		*/
		'config': {
			'static_path': '/_static/module/tuvedi',
			'command_path': '/tuvedi',
			'lang': 'en',
			'device': 0,
			'refresh': 60000,
			'animation.type': 'fade',
			'animation.speed': 'normal'
		},

		/**
		Get the value for the given config option

		@function {public  mixed-type} ?
		@param {String} id - The name of the config option
		@param {mixed-type} default_value - The value to use if no value for the config option is set.
		@return The value of the config option | The default_value if the config option doesn't exist.
		*/
		'get': function (id, default_value) {
			if (this.config[id] === undefined) {
				return default_value;
			} else {
				return this.config[id];
			}
		},

		/**
		Update the internal configuration.

		@function {public} ?
		@param {Array} conf - An array with the config options
		*/
		update: function (conf) {
			jQuery.extend(this.config, conf);
		}
	};
}());
/**
This class provides some function to load resources.

@class TuVedi.Resource
*/
(function () {
	TuVedi.Resource = {
		/**
		@var {Function} callback The callback function
		*/
		callback: undefined,

		/**
		@var {Integer} unfinished number of files to load
		*/
		unfinished: 0,

		/**
		@var {List} list of libs loaded by require() function
		*/
		requirements_loaded: [],

		/**
		Use a special function to load something.

		@function {public} ?
		*/
		loadFunction: function (func) {
			this.unfinished++;
			func.apply(this,
				[
					function () {
						TuVedi.Resource.unfinished--;
						if (TuVedi.Resource.unfinished === 0 && TuVedi.Resource.callback !== undefined) {
							var callb = TuVedi.Resource.callback;
							TuVedi.Resource.callback = undefined;
							callb();
						}
					}
				]
			);
		},

		/**
		Load JavaScript files dynamically.

		@function {public} ?
		@param {String} [optional params] - This function uses the join function from the url class to join the given params to a valid url and loads the script
		*/
		loadScript: function () {
			var head = document.getElementsByTagName("head")[0];
			var script = document.createElement("script");

			// join the arguments to get an valid url
			script.src = TuVedi.URL.join.apply(this, arguments);
			//alert(script.src);
			if(script.src.match(/^file:\/\//i) === null) {
				var done = false;
				this.unfinished++;
				script.onload = script.onerror = script.onreadystatechange = function () {
					if (!done && (!this.readyState || this.readyState === "loaded" || this.readyState === "complete")) {
						done = true;

						// Handle memory leak in IE
						script.onload = script.onreadystatechange = function () {};
						//head.removeChild( script );
						TuVedi.Resource.unfinished--;
						if (TuVedi.Resource.unfinished === 0 && TuVedi.Resource.callback !== undefined) {
							var callb = TuVedi.Resource.callback;
							TuVedi.Resource.callback = undefined;
							callb();
						}
						//alert(this.readyState + this.src);
					}
				};
			}
			head.appendChild(script);
		},

		/**
		Load CSS files dynamically.
		@function {public} ?
		@param {String} [optional params] - This function uses the join function from the url class to join the given params to a valid url and loads the file
		@since 0.3
		*/
		loadStyle: function (url) {
			var head = document.getElementsByTagName("head")[0];
			var style = document.createElement("link");
			style.rel = "stylesheet";
			style.type = "text/css";

			// join the arguments to get an valid url
			style.href = TuVedi.URL.join.apply(this, arguments);

			head.appendChild(style);
		},

		/**
		Wait until all given scripts and css files are loaded an call the callback function.

		@function {public} ?
		@param {Function} callb - The callback function
		@since 0.3
		*/
		onReady: function (callb) {
			if (this.unfinished === 0) {
				this.callback = undefined;
				callb();
			} else {
				this.callback = callb;
			}
		},

		/**
		Load all given libs

		@function {public} ?
		@param {String} [optional params] - Names of the required libs
		*/
		require: function() {
			var i, lib_name;
			for(i=0; i < arguments.length; i++) {
				lib_name = arguments[i];
				if	(jQuery.inArray(lib_name, this.requirements_loaded) < 0) {
					this.requirements_loaded.push(lib_name);
					this.loadScript(TuVedi.Config.get("static_path"), "lib", lib_name + ".js");
				}
			}
		}
	};
}());
/**
Handle all the URL stuff for us.

@class TuVedi.URL
*/
(function () {
	TuVedi.URL = {
		/**
		Encode an URL

		@function {public String} ?
		@return The URL
		*/
		'encode': function (url, params) {
			return url + "?" + jQuery.param(params);
		},

		/**
		Join an URL

		@function {public String} ?
		@return The URL
		*/
		'join': function () {
			// loop var
			var i;
			var args = arguments;
			var tmp = [];
			var arg;
			for (i = 0; i < args.length; i++) {
				arg = args[i];
				if (arg !== undefined) {
					if(typeof(arg) !== 'string') {
						if(arg.toString !== undefined) {
							arg = arg.toString()
						} else {
							arg = arg + '';
						}
					}
					if (i > 0) {
						if (arg.charAt(0) === '/') {
							arg = arg.substring(1, arg.length);
						}
					}
					if (arg.charAt(arg.length - 1) === '/') {
						arg = arg.substring(0, arg.length - 1);
					}
					tmp.push(arg);
				}
			}
			tmp = tmp.join('/');
			if (tmp.charAt(0) === '/') {
				return tmp;
			} else if (tmp.match(/^http:\/\//i) || tmp.match(/^https:\/\//i) || tmp.match(/^file:\/\//i)) {
				return tmp;
			} else {
				var command_path = TuVedi.Config.get('command_path');
				//check if the base_url is already in the generated url
				var re = new RegExp('^' + command_path);
				if (re.test(tmp)) {
					return tmp;
				} else {
					if (command_path.charAt(command_path.length - 1) !== '/') {
						command_path = command_path + '/';
					}
					return commmand_path + tmp;
				}
			}
		},

		/**
		Join an URL for the TuVedi e.g. for an update request

		@function {public String} ?
		@return The URL.
		*/
		joinTuVedi: function() {
			var args = [TuVedi.Config.get("command_path")]
			args = args.concat(Array.prototype.slice.call(arguments));
			return this.join.apply(this,  args);
		}
	};
}());