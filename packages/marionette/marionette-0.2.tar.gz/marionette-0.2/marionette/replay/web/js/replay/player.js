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
replay.isPlayer = function(type) {
    return type === 'Player';
};


replay.Player = function(options) {
    // create empty animation
    var canvas = document.createElement('canvas');
    canvas.src = 'empty';
    canvas.width = 20;
    canvas.height = 20;
    var anim = new jaws.Animation({
        sprite_sheet: canvas,
        frame_size: [20, 20],
        frame_duration: 100,
    });
    this.intent = 'default'
    var newoptions = $.extend({
        anims: {'default': anim},
        layer: 4,
        color: options.playernum % replay.tints.length,
    }, options);
    replay.Sprite.call(this, newoptions);
}
replay.Player.prototype = new replay.Sprite({});
replay.Player.prototype.constructor = replay.Player;


replay.Player.prototype.drawName = function() {
    this.context.font = 'bold 20px sans-serif';
    this.context.fillStyle = replay.tints[this.color];
    var x = 175 * this.playernum + 10 + this.viewport.x;
    var y = this.context.canvas.height - 10 + this.viewport.y;
    var name = this.name;
    if (this.name.length > 12) {
        name = this.name.substring(0, 11) + '...';
    }
    this.context.fillText(name, x, y);
};


replay.Player.prototype.changeEnd = function(timefrac) {
    this.round_died = this.round;
}
