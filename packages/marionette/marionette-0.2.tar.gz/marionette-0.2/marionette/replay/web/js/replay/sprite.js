/*
 *   Copyright 2011 Inkylabs et al.
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 *
 * <Insert Marionetastical limerick here>
 *
 */
replay.Sprite = function(options) {
    jaws.Sprite.call(this, {});
    this.intVars = ['x', 'y'].concat(options.intVars || []);
    var change = $.extend({}, options);
    this.anims = {};
    var that = this;
    for (key in change.anims) {
        this.anims[key] = change.anims[key].slice();
        if (key === 'die') {
            this.anims[key].on_end = function() {
                that.end = true;
            };
        }
    }
    delete change.intVars;
    delete change.anims;
    this.change(change);
    this.prevIntent = null;
};
replay.Sprite.prototype = new jaws.Sprite({});
replay.Sprite.prototype.constructor = replay.Sprite;

replay.Sprite.prototype.updateInts = function(timefrac) {
    for (var i = 0; i < this.intVars.length; i++) {
        var name = this.intVars[i];
        var prev = this[name + 'Prev'];
        var next = this[name + 'Next'];
        this[name] = parseInt(prev + timefrac * (next - prev));
    }
};

replay.Sprite.prototype.updateAnim = function(timefrac) {
    var curAnim = this.anims[this.intent] || this.anims['default'];
    if (curAnim !== this.anim) {
        this.anim = curAnim;
        this.anim.index = 0;
    }
    this.setImage(this.anim.next());
};

replay.Sprite.prototype.update = function(round, timefrac) {
    // The round passed to us is the round that we don't yet have info about
    round--;
    // Update all special variables needing to be updated
    if (round > this.round) {
        this.round = round;
        for (var i = 0; i < this.intVars.length; i++) {
            var name = this.intVars[i];
            this.doDefaultChange(name, this[name + 'Next']);
        }
    }

    // Call all update methods
    for (var name in this) {
        if (name.indexOf('update') === 0 &&
            name !== 'update' &&
            name !== 'updateDiv' &&
            typeof(this[name]) === 'function') {
            this[name](timefrac);
        }
    }
};

replay.Sprite.prototype.doDefaultChange = function(name, val) {
    var prev = name + 'Prev';
    var next = name + 'Next';
    if (this[next] === undefined) {
        this[prev] = val;
    } else {
        this[prev] = this[next];
    }
    this[next] = val;
    this.defaultChangesMade.push(name);
}

replay.Sprite.prototype.changeEnd = function(end) {
    if (this.anims.die) {
        return;
    }
    this.end = end;
};

replay.Sprite.prototype.changePos = function(pos) {
    this.doDefaultChange('x', pos[0]);
    this.doDefaultChange('y', pos[1]);
};

replay.Sprite.prototype.change = function(change) {
    this.defaultChangesMade = [];

    for (var name in change) {
        var firstChar = name.substr(0, 1).toUpperCase();
        var fname = 'change' + firstChar + name.substr(1)
        if (typeof(this[fname]) === 'function') {
            this[fname](change[name]);
        } else if (this.intVars.indexOf(name) === -1) {
            this[name] = change[name];
        } else {
            this.doDefaultChange(name, change[name]);
        }
    }

    // Make changes for all intVars
    for (var i = 0; i < this.intVars.length; i++) {
        var name = this.intVars[i];
        if (this.defaultChangesMade.indexOf(name) === -1) {
            this.doDefaultChange(name, this[name + 'Next']);
        }
    }
};

replay.Sprite.prototype.draw = function() {
    for (var name in this) {
        if (name.indexOf('draw') === 0 &&
            name !== 'draw' &&
            typeof(this[name]) === 'function') {
            this[name]();
        }
    }
    jaws.Sprite.prototype.draw.call(this);
};
