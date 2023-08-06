/* http://net.tutsplus.com/tutorials/javascript-ajax/creating-a-keyboard-with-css-and-jquery/ */
define([
	], function() {
		var Keyboard = Backbone.View.extend({

			capslock: false,
			disabledKeys: false,

			initialize: function () {
				this.target = this.options.target;
				this.$target = $(this.options.target);
				this.disabledKeys = this.options.disabledKeys;
				this.capslock = this.options.capslock;
				this.el = this.options.el;
			},

			setTarget: function (target) {
				if (this.$target !== undefined) {
					this.$target.removeClass('focus');
				}
				this.target = target;
				this.$target = $(target);
				this.$target.addClass('focus');
			},

			render: function () {
				this.$el = $(this.el);
				var self = this;
				if (this.capslock) {
					this.$('.letter').toggleClass('uppercase');
					this.$('.capslock').addClass('active');
				}
				$.each(this.disabledKeys, function(id, key) {
					self.$('.' + key).addClass('disabled');
				});

				this.$('li').mousedown(function (event) {
					var $this = $(this),
					character = $this.html(); // If it's a lowercase letter, nothing happens to this variable


					// Disabled keys
					if ($this.hasClass('disabled')) {
						return false;
					}

					// Shift keys
					if ($this.hasClass('left-shift') || $this.hasClass('right-shift')) {
						self.$('.letter').toggleClass('uppercase');
						self.$('.shift').toggleClass('active');
						self.$('.symbol span').toggle();

						self.shift = (self.shift === true) ? false : true;
						return false;
					}

					// Caps lock
					if ($this.hasClass('capslock')) {
						self.$('.letter').toggleClass('uppercase');
						$this.toggleClass('active');
						self.capslock = (self.capslock === true) ? false : true;
						return false;
					}

					// Backspace
					if ($this.hasClass('backspace')) {
						var content = self.$target.val();
						self.$target.val(content.substr(0, content.length - 1));
						return false;
					}

					// Special characters
					if ($this.hasClass('symbol')) character = $('span:visible', $this).html();
					if ($this.hasClass('space')) character = ' ';
					if ($this.hasClass('tab')) character = "\t";
					if ($this.hasClass('return')) character = "\n";

					// Uppercase letter
					if ($this.hasClass('uppercase')) character = character.toUpperCase();

					// Remove shift once a key is clicked.
					if (self.shift === true) {
						self.$('.symbol span').toggle();
						self.$('.letter').toggleClass('uppercase');
						self.$('.shift').toggleClass('active');
						self.shift = false;
					}

					// Add the character
					self.$target.val(self.$target.val() + character);

					//show tooltip with the character
					var p = $('<p>').html(character);
					p.addClass('tooltip').addClass('ui-corner-all').css({
						opacity: 0.9
					});
					
					p.css({
						width: 20,
						height: 20,
						textAlign: 'center',
						lineHeight: '100%',
						position: 'absolute',
						left: event.clientX - 10,
						top: event.clientY - 70
					});
					$('body').append(p);
					p.show();
					var remove = function () {
						p.hide();
						p.remove();
					};

					$this.mouseup(remove);

					$this.mouseout(remove);
					
					return true;
				});

			}
		});
		return Keyboard;
	});