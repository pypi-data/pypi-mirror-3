;(function($){
	function Fullscreen(el, opts){
		self = this
		self.el = $(el);
		self.defaults = {};
		self.opts = $.extend(self.defaults, opts);
		self.init();
	}
	Fullscreen.prototype.init = function(){
		// set original height and width
		self.original_width = self.el.width();
		self.original_height = self.el.height();
		// set the icon up
		self.icon = $('<a>', {className: 'fullscreen'});
		self.icon.click(self.dispatch)
		self.el.before(self.icon);
		// add the class names
		self.el.parent().addClass('fullscreen-container');
		// bind the escape key to _deactivate
		Mousetrap.bind('esc', self._deactivate);
		// add the mousetrap class so that esc fires deactivate
		self.el.addClass('mousetrap');
		// handle tabs
		self.el.keydown(function(e) {
			if(e.keyCode === 9) { // tab was pressed
				var start = this.selectionStart;
					end = this.selectionEnd;
				var $this = $(this);
				$this.val($this.val().substring(0, start)
							+ "\t"
							+ $this.val().substring(end));
				this.selectionStart = this.selectionEnd = start + 1;
				// prevent the focus lose
				return false;
			}
		});
	}
	/* 
	 * handle tabs
	 */
	/*
	 * Activate the fullscreen
	 */
	Fullscreen.prototype._activate = function(e){
		self.el.parent().addClass('active')
	}
	/*
	 * Deactivate the fullscreen
	 */
	Fullscreen.prototype._deactivate = function(e){
		self.el.parent().removeClass('active')
	}
	/*
	* when the icon is clicked
	*/
	Fullscreen.prototype.dispatch = function(e){
		if(self.el.parent().hasClass('active')){
			self._deactivate(e);
		}else{
			self._activate(e);
		}
	}
	/* 
	* register the plugin
	*/
	$.fn.omfs = function(opts) {
		return this.each(function() {
			new Fullscreen(this, opts);
		});
	};
})( django.jQuery );



// now call it
django.jQuery(function($){
    $('textarea.fullscreen').omfs();
});
