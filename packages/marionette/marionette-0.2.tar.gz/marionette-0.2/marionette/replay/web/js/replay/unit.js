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
 * Some babies are known for their crawling,
 * but he, for his loud caterwauling.
 *    Why would you desire
 *    this petulant crier?
 * Because when he's quiet, he's dah-ling.
 *
 */
replay.initializeUnitAnimations = function() {
    replay.unitAnimations = replay.createAnimations('units', {
        brawlmander: {
            frameSize: [30, 30],
            modes: {
                attackN: {frames: [32, 40]},
                attackNE: {extend: 'attackN'},
                attackE: {extend: 'attackN'},
                attackSE: {extend: 'attackN'},
                attackS: {extend: 'attackN'},
                attackSW: {extend: 'attackN'},
                attackW: {extend: 'attackN'},
                attackNW: {extend: 'attackN'},
                'default': {extend: 'idle'},
                die: {frames: [4, 12], loop: false},
                idle: {frames: [0, 4]},
                moveN: {frames: [12, 16]},
                moveNE: {frames: [16, 20]},
                moveE: {frames: [20, 24]},
                moveSE: {frames: [24, 28]},
                moveS: {frames: [28, 32]},
                moveSW: {extend: 'moveSE', flipX: true},
                moveW: {extend: 'moveE', flipX: true},
                moveNW: {extend: 'moveNE', flipX: true},
            },
        },
        toad: {
            frameSize: [30, 30],
            modes: {
                'default': {extend: 'idle'},
                die: {frames: [4, 12], loop: false},
                idle: {frames: [0, 4]},
                moveN: {frames: [12, 16]},
                moveNE: {frames: [16, 20]},
                moveE: {frames: [20, 24]},
                moveSE: {frames: [24, 28]},
                moveS: {frames: [28, 32]},
                moveSW: {extend: 'moveSE', flipX: true},
                moveW: {extend: 'moveE', flipX: true},
                moveNW: {extend: 'moveNE', flipX: true},
            },
        },
    }, {
        tinted: true,
    });
};


replay.isUnit = function(type) {
    return type in this.unitAnimations;
};


replay.Unit = function(options) {
    replay.Sprite.call(this, $.extend({
        anims: replay.unitAnimations[options.type][options.player.color],
        intVars: ['health', 'maxHealth'],
        layer: 2,
        pos: [0, 0],
    }, options));
    // FUTURE: Remove this when bug is fixed.
    this.anims.die.loop = false;
};
replay.Unit.prototype = new replay.Sprite({});
replay.Unit.prototype.constructor = replay.Unit;


replay.Unit.prototype.drawHealth = function() {
    this.context.fillStyle = '#000000';
    if (this.anim.currentFrame() === undefined) {
        a = 4;
    }
    var unitHeight = this.anim.currentFrame().height;
    var barHeight = parseInt(this.maxHealth / 10) + 2;
    this.context.fillRect(this.x - 7, this.y + unitHeight - barHeight,
                            5, barHeight);
    this.context.fillStyle = '#ffffff';
    barHeight -= 2;
    this.context.fillRect(this.x - 6, this.y + unitHeight - barHeight - 1,
                            3, barHeight);
    var p = this.health / this.maxHealth;
    this.context.fillStyle = replay.greenRedScale(p);
    barHeight = parseInt(this.health / 10);
    this.context.fillRect(this.x - 6, this.y + unitHeight - barHeight - 1,
                          3, barHeight);
};
