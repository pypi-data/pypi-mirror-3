(function($) {
	$.fn.tuvediTextFill = function(options) {
		var fontSize = options['maxFontPixels'];
		var minFontSize = options['minFontPixels'];
		var container = options['container'];
		var maxHeight = options['maxHeight'];
		var maxWidth = options['maxWidth'];

		if(minFontSize === undefined) {
			minFontSize = 4;
		}

		var textHeight;
		var textWidth;
		this.each(function(){
			var $this = $(this);
			if(options['sameSize'] !== true) {
				fontSize = options['maxFontPixels'];
			}
			if(container === undefined) {
				container = $this.parent();
			}

			if(maxHeight === undefined) {
				maxHeight = container.height();
			}
			
			if(maxWidth === undefined) {
				maxWidth = container.width();
			}
			do {
				$this.css('font-size', fontSize);
				textHeight = $this.height();
				textWidth = $this.width();
				fontSize = fontSize - 1;
			} while (textHeight > maxHeight || textWidth > maxWidth && fontSize > minFontSize);
		});

		if(options['sameSize'] === true) {
			this.each(function(){
				var $this = $(this);
				$this.css('font-size', fontSize);
			});
		}

		return this;
	}
})(jQuery);
