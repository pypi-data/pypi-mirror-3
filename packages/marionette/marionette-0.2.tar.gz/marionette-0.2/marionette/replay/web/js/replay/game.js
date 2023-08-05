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
replay.Game = function() {
    this.canvas = $('#' + replay.options.canvasId);
    this.sprites = {};
    this.layers = [{}, {}, {}, {}, {}];
    this.viewport = null;
    this.rounds = [];
    this.curround = 0;
    this.roundtime = 100;
    this.lastroundinc = 0;
    this.players = [];
    this.loadingdiv = null;
    this.gameover = false;

    // GameLoop detaches these functions from their original object, so we do
    // the following:
    var game = this;
    this.setup = function() {
        replay.Game.prototype.setup.call(game);
    };
    this.update = function() {
        replay.Game.prototype.update.call(game);
    };
    this.draw = function() {
        replay.Game.prototype.draw.call(game);
    };
};

replay.Game.prototype.setup = function() {
    // Assemble the rounds
    // The cumulative number of rounds prior to each file
    var cumulativeRounds = [0];
    var game = this;
    $.doTimeout('round_assembler', 5000, function() {
        // If we are finished, go ahead and exit
        if (game.rounds.length > 0 &&
            game.rounds[game.rounds.length - 1].end === true) {
            return false;
        }

        // Construct the url
        var curfilenum = cumulativeRounds.length - 1;
        var url = replay.options.replayUrl + '/' + curfilenum;
        if (replay.options.bust_cache) {
            url += '?' + new Date().getTime();
        }

        // Get the file
        $.getJSON(url, function(data) {
            var prevRounds = cumulativeRounds[curfilenum];
            var totalRounds = prevRounds + data.length;
            cumulativeRounds[curfilenum + 1] = totalRounds;
            // We insert these directly instead of just calling concat to
            // handle the case where this function gets called twice with
            // the same curfilenum
            for (var i = 0; i < data.length; i++) {
                game.rounds[prevRounds + i] = data[i];
            }
        });
        return true;
    });
    // Start the round assembler immediately
    $.doTimeout('round_assembler', true);

    // Initialize animations
    replay.initializeUnitAnimations();
    replay.initializeItemAnimations();
    replay.initializeBackgroundAnimations();

    // Create the loading div
    var offset = this.canvas.offset();
    this.loadingdiv = $('<div>');
    loadgifurl = replay.options.mediaPrefix + 'load.gif';
    this.loadingdiv.css({
        'background-image': 'url(' + loadgifurl + ')',
        'background-position': 'center center',
        'background-repeat': 'no-repeat',
        'background-color': '#444444',
        width: this.canvas.css('width'),
        height: this.canvas.css('height'),
        position: 'absolute',
        left: offset.left,
        top: offset.top,
        opacity: 0.4,
    });
    this.loadingdiv.hide();
    $('body').append(this.loadingdiv);
};

replay.Game.prototype.update = function() {
    // Wait on more rounds if we need to
    if (!this.rounds[this.curround] && !this.gameover) {
        this.loadingdiv.show();
        return;
    }
    this.loadingdiv.hide();

    // Get changes
    var timestamp = new Date().getTime();
    var timefrac = (timestamp - this.lastroundinc) / this.roundtime;
    var incround = false;
    var changes = {};
    if (timefrac > 1.0) {
        incround = true;
        this.lastroundinc = timestamp;
        timefrac = 0.0;
        if (!this.gameover) {
            changes = this.rounds[this.curround];
        }
    }

    // Handle changes to sprites
    var handled = {};
    for (var key in changes) {
        this.handleChange(key, changes, handled);
    }

    // Increment the current round
    if (incround) {
        this.curround++;
    }

    // Handle basic updates
    for (var id in this.sprites) {
        this.sprites[id].update(this.curround, timefrac);
        if (this.sprites[id].end) {
            delete this.layers[this.sprites[id].layer][id];
            delete this.sprites[id];
        }
    }

    // Update the viewport
    replay.updateViewport(this.viewport);

    // Draw the scoreboard if necessary
    if (this.gameover && !('scoreboard' in this.sprites)) {
        var show_scoreboard = true;
        for (var id in this.sprites) {
            if (this.sprites[id].intent === 'die') {
                show_scoreboard = false;
                break;
            }
        }
        if (show_scoreboard) {
            this.addSprite('scoreboard', new replay.Scoreboard({
                viewport: this.viewport,
                winner_str: this.winner_str
            }));
        }
    }
};

replay.Game.prototype.addSprite = function(key, sprite) {
        this.sprites[key] = sprite;
        this.layers[sprite.layer][key] = sprite;
};

replay.Game.prototype.handleChange = function(key, changes, handled) {
    if (key in handled) {
        return;
    }
    var change = changes[key];
    if (key === 'dimensions') {
        world = new jaws.Rect(0, 0, change[0], change[1]);
        this.viewport = replay.createViewport(world, this.canvas);
        this.addSprite('background', new replay.Background);
        this.addSprite('dashboard', new replay.Dashboard({
            viewport: this.viewport,
        }));
    } else if (key === 'end') {
        this.gameover = change;
        for (var i = 0; i < this.players.length; i++) {
            if (this.players[i].round_died === undefined) {
                this.players[i].round_died = this.curround + 1;
            }
        }
        this.players.sort(function(p1, p2) {
            return p1.round_died - p2.round_died;
        })
        var winner = this.players.pop()
        var winners = [winner.name];
        var max_round = winner.round_died;
        for (var i = this.players.length - 1; i >= 0; i--) {
            if (this.players[i].round_died === max_round) {
                winners.push(this.players[i].name);
            } else {
                break;
            }
        }
        this.winner_str = winners.join(', ');
    } else {
        change.round = this.curround;
        change.id = parseInt(key);
        if (!(key in this.sprites)) {
            if (replay.isUnit(change.type)) {
                if (!(change.player in this.sprites)) {
                    this.handleChange(change.player, changes, handled);
                }
                change.player = this.sprites[change.player];
                this.addSprite(key, new replay.Unit(change));
            } else if (replay.isItem(change.type)) {
                this.addSprite(key, new replay.Item(change));
            } else if (replay.isPlayer(change.type)) {
                if (!('dimensions' in this.sprites)) {
                    this.handleChange('dimensions', changes, handled);
                }
                change.playernum = this.players.length;
                change.viewport = this.viewport;
                this.addSprite(key, new replay.Player(change));
                this.players.push(this.sprites[key])
            }
        } else {
            this.sprites[key].change(change);
        }
    }
    handled[key] = true;
};

replay.Game.prototype.draw = function() {
    var width = this.canvas.width();
    this.canvas.attr('width', width);
    var height = this.canvas.height();
    this.canvas.attr('height', height);

    if (this.curround === 0) {
        return;
    }

    this.viewport.width = width;
    this.viewport.height = height;

    jaws.clear();

    var layers = this.layers;
    this.viewport.apply(function() {
        for (var i = 0; i < layers.length; i++) {
            for (var id in layers[i]) {
                layers[i][id].draw();
            }
        }
    });
};
