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
replay.Scoreboard = function(options) {
    options = options || {};
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
        endRound: Infinity,
        pos: [0, 0],
        layer: 3,
    }, options);
    replay.Sprite.call(this, newoptions);
};
replay.Scoreboard.prototype = new replay.Sprite({});
replay.Scoreboard.prototype.constructor = replay.Scoreboard;


replay.Scoreboard.prototype.drawScoreboard = function() {
    var scoreHeight = 150;
    var scoreWidth = 600;
    var scoreXPos = Math.round((this.viewport.width - scoreWidth) / 2) +
                    this.viewport.x;
    var scoreYPos = Math.round((this.viewport.height - scoreHeight) / 2) +
                    this.viewport.y;
    this.context.fillStyle = '#bbbbbb';
    this.context.fillRect(scoreXPos, scoreYPos, scoreWidth, scoreHeight);
    this.context.fillStyle = '#000000';
    this.context.font = 'bold 30px sans-serif';
    this.context.fillText(this.winner_str + " won!", scoreXPos + 20,
                          scoreYPos + 50);
};
