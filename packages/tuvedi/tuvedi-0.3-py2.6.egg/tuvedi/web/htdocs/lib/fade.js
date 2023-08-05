(function($) {
	var methods = {
		init: function(options) {
			var defaults = {
				'animation.type': TuVedi.Config.get('animation.type'),
				'animation.speed': TuVedi.Config.get('animation.speed'),
				'type': 'sequence',
				'timeout': 10000,
				'containerHeight': '100%'
			};

			if (options === undefined) {
				var options = {}
			}

			var options = $.extend(defaults, options);

			if(jQuery.inArray(options['type'], ["random", "sequence"]) === null) {
				options['type'] = "sequence";
			}
			if(jQuery.inArray(options['animation.type'], ["fade", "slide"]) === null) {
				options['animation.type'] = "fade";
			}
			
			return this.each(function(){
				var $this = $(this);

				var elements = $this.children();

				if (elements.length > 1) {
					$this.css('position', 'relative').css('height', options.containerheight);
					for (var i = 0; i < elements.length; i++) {
						$(elements[i]).css('z-index', String(elements.length-i)).css('position', 'absolute').hide();
					};

					if (options['type'] === "random") {
						var current = Math.floor ( Math.random () * ( elements.length ) );
						$this.tuvediFade("next", elements, options, current, 0);
					} else if (options['type'] === "sequence") {
						$this.tuvediFade("next", elements, options, 0, 0);
					} 
				}
			});
		},
		next: function(elements, options, current, last, session_id) {
			var $this = $(this);

			if(session_id === undefined) {
				session_id = new Date().getTime();
				$this.data('tuvediFade.session_id', session_id);
			} else if(session_id !== $this.data('tuvediFade.session_id')) {
				return;
			}

			if (options['animation.type'] === 'slide') {
				$(elements[last]).slideUp(options['aninmation.speed']);
				$(elements[current]).slideDown(options['animation.speed']);
			} else if (options['animation.type'] === 'fade') {
				$(elements[last]).fadeOut(options['animation.speed']);
				$(elements[current]).fadeIn(
					options['animation.speed'],
					function() {
						// IE: remove the opacity-filter
						if($(this)[0].style.removeAttribute){
							$(this)[0].style.removeAttribute('filter');
						}
					}
				);
			}

			var last = current;
			if (options['type'] === "sequence") {
				if ((current + 1) < elements.length) {
					current = current + 1;
				} else {
					current = 0;
				}
			} else if (options['type'] === "random") {
				while (current === last) {
					current = Math.floor(Math.random() * elements.length);
				}
			}

			setTimeout(
				function() {
					$this.tuvediFade("next", elements, options, current, last, session_id);
				},
				options.timeout
			);
		}
	};

	$.fn.tuvediFade = function(method) {
		if ( methods[method] ) {
			return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
		} else if ( typeof method === 'object' || ! method ) {
			return methods.init.apply( this, arguments );
		} else {
			$.error( 'Method ' +  method + ' does not exist.' );
		}    
	}

})(jQuery);
