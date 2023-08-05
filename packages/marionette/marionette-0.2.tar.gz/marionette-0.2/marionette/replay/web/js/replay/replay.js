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

/**
 * Replay is a wrapper around the Game class that we pass to jaws.
 *
 * canvasId:
 *   {String} The canvas id for the world
 */
replay.Replay = function(canvasId, replayUrl, mediaPrefix, bust_cache) {
    // Set some options since we can't pass Game parameters
    replay.options = {
        canvasId: canvasId,
        replayUrl: replayUrl,
        mediaPrefix: mediaPrefix,
        bust_cache: bust_cache,
    };

    // Start jaws

    jaws.assets.root = mediaPrefix;
    jaws.assets.add([
        'backgrounds/default.png',
        'items/grutonium.png',
        'units/brawlmander.png',
        'units/toad.png',
    ]);
    jaws.start(replay.Game, {
        'loading_screen': false,
    });
};
