define([
	], function() {

		var Batch = function (size) {
			this.size = size;
			this.successed = {};
			this.failed = {};

			this.success = function (id) {
				this.successed[id] = true;
			};

			this.fail = function (id) {
				this.failed[id] = true;
			};

			this.ended = function () {
				return (Object.keys(this.successed).length + Object.keys(this.failed).length === this.size);
			};

			this.wasSuccessful = function () {
				return (Object.keys(this.successed).length === this.size)
			}

			this.allFailed = function () {
				return Object.keys(this.failed);
			}

		};

		var BatchOperations = {

			batches: {},

			register: function (size) {
				var key = this._generateKey();
				while (this.batches[key] !== undefined) {
					key = this._generateKey();
				}
				this.batches[key] = new Batch(size);
				return key;
			},

			_generateKey: function () {
				return (((Math.random())*0x10000)|0);
			},

			success: function (batchid, id) {
				if (this.batches[batchid] !== undefined) {
					this.batches[batchid].success(id)
				}
			},

			fail: function (batchid, id) {
				if (this.batches[batchid] !== undefined) {
					this.batches[batchid].fail(id)
				}
			},

			result: function (batchid) {
				var batch = this.batches[batchid];
				if (batch !== undefined) {
					if (batch.ended()) {
						if (batch.wasSuccessful()) {
							return true;
						} else {
							return batch.allFailed();
						}
					}
				}
				return false;
			}
		};

		return BatchOperations;
	});