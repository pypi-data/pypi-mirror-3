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
replay.createViewport = function(world, canvas) {
    var mousedown = false;
    viewport = new jaws.Viewport({
        min_x: 0,
        min_y: 0,
        max_x: world.width,
        max_y: world.height + 30,
    });
    viewport.world = world;
    viewport.canvas = canvas;

    // Listen for click events
    function updateDrag(x, y) {
        if (canvas.width() < world.width) {
            viewport.x -= x - lastdrag[0];
        }
        if (canvas.height() < world.height) {
            viewport.y -= y - lastdrag[1];
        }
        lastdrag = [x, y];
    }

    // Attach focus and blur events
    viewport.in_focus = false;
    var click_data = {timeStamp: 0}
    $("body").click(function(e) {
        if (e.timeStamp - click_data.timeStamp > 500 ||
            e.clientX != click_data.clientX ||
            e.clientY != click_data.clientY) {
            viewport.in_focus = false;
        }
    })
    $("canvas").click(function(e) {
        viewport.in_focus = true;
        click_data = e;
    })
    canvas.mousedown(function(e) {
        mousedown = true;
        lastdrag = [e.pageX, e.pageY];
    });
    $(document).mouseup(function(e) {
        if (mousedown) {
            mousedown = false;
            updateDrag(e.pageX, e.pageY);
        }
    });
    $(document).mousemove(function(e) {
        if (mousedown) {
            updateDrag(e.pageX, e.pageY);
        }
    });
    $(document).hover(null, function(e) {
        if (mousedown) {
            mousedown = false;
            updateDrag(e.pageX, e.pageY);
        }
    });
    $(document).keydown(function(e) {
        if (viewport.in_focus) {
            e.preventDefault();
        }
    });
    $(document).keypress(function(e) {
        if (viewport.in_focus) {
            e.preventDefault();
        }
    });

    // Return
    return viewport;
};


replay.updateViewport = function(viewport) {
    var arrow_key_speed = 15;
    if (viewport.in_focus) {
        if (jaws.pressed("left"))  {
            viewport.x -= arrow_key_speed;
        }
        if (jaws.pressed("right"))  {
            viewport.x += arrow_key_speed;
        }
        if (jaws.pressed("down"))  {
            viewport.y += arrow_key_speed;
        }
        if (jaws.pressed("up"))  {
            viewport.y -= arrow_key_speed;
        }
    }
    viewport.verifyPosition();
    if (viewport.canvas.width() > viewport.world.width) {
        var extra = viewport.canvas.width() - viewport.world.width;
        viewport.x = -parseInt(extra / 2);
    }
    if (viewport.canvas.height() > viewport.world.height) {
        var extra = viewport.canvas.height() - viewport.world.height;
        viewport.y = -parseInt(extra / 2);
    }
}


replay.initializeBackgroundAnimations = function() {
    replay.backgroundAnimations = replay.createAnimations('backgrounds', {
        'default': {
            frameSize: [900, 600],
            modes: {
                'default': {extend: 'idle'},
                idle: {frames: [0, 1]},
            },
        },
    });
};


replay.Background = function(options) {
    options = options || {};
    this.intent = 'default';
    replay.Sprite.call(this, $.extend({
        anims: replay.backgroundAnimations['default'],
        endRound: Infinity,
        layer: 0,
        pos: [0, 0],
    }, options));
};
replay.Background.prototype = new replay.Sprite({});
replay.Background.prototype.constructor = replay.Background;
