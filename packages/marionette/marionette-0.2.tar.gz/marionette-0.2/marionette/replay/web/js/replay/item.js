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
replay.initializeItemAnimations = function() {
    replay.itemAnimations = replay.createAnimations('items', {
        grutonium: {
            frameSize: [20, 20],
            modes: {
                'default': {extend: 'idle'},
                idle: {frames: [0, 7], bounce: true},
                die: {frames: [7, 8], loop: false},
            },
        },
    });
};


replay.isItem = function(type) {
    return type in this.itemAnimations;
};


replay.Item = function(options) {
    replay.Sprite.call(this, $.extend({
        anims: replay.itemAnimations[options.type],
        layer: 1,
    }, options));
    // FUTURE: Remove this when bug is fixed.
    this.anims.die.loop = false;
};
replay.Item.prototype = new replay.Sprite({});
replay.Item.prototype.constructor = replay.Item;
