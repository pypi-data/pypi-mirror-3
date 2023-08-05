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
replay = {};


replay.fromCamelCase = function(name) {
    var ret = name.charAt(0).toLowerCase();
    for (var i = 1; i < name.length; i++) {
        lower = name.charAt(i).toLowerCase();
        if (name.charAt(i) != lower) {
            ret += '_';
        }
        ret += lower;
    }
    return ret;
};


replay.createAnimationsFromAsset = function(asset, frameSize, modes) {
    var orig = new jaws.Animation({
        sprite_sheet: asset,
        frame_size: frameSize,
        frame_duration: 100,
    });
    var flipped = new jaws.Animation({
        sprite_sheet: replay.transformAsset(asset, {'flipX': true}),
        frame_size: frameSize,
        frame_duration: 100,
    });

    var ret = {};
    for (var name in modes) {
        var mode = modes[name];
        if (mode.extend) {
            mode = $.extend({}, modes[mode.extend], mode);
        }
        var anim = mode.flipX ? flipped : orig;
        var frames = mode.frames;
        ret[name] = anim.slice(frames[0], frames[1]);
        var attrs = [
            'loop',
            'bounce',
        ];
        for (var i = 0; i < attrs.length; i++) {
            if (attrs[i] in mode) {
                ret[name][attrs[i]] = mode[attrs[i]];
            }
        }
    }
    return ret;
};


replay.tints = [
    '#ff0000',
    '#0000ff',
    '#ffffff',
    '#000000',
    '#500050',
    '#e25c00',
    '#ffff00',
    '#500000',
    '#000050',
    '#ff00ff',
];


replay.createAnimations = function(dir, types, globalOptions) {
    var ret = {};
    var prefix = dir + '/';
    globalOptions = globalOptions || {};
    for (var type in types) {
        var baseName = prefix + replay.fromCamelCase(type) + '.png';
        var options = $.extend(globalOptions, types[type]);

        // No tints
        if (options.tinted !== true) {
            ret[type] = replay.createAnimationsFromAsset(
                    baseName,
                    options.frameSize,
                    options.modes);
            continue;
        }

        // Load all tints
        ret[type] = [];
        for (var i = 0; i < replay.tints.length; i++) {
            jaws.assets.loadTintedAsset(baseName, replay.tints[i]);
            ret[type].push(replay.createAnimationsFromAsset(
                    baseName + replay.tints[i],
                    options.frameSize,
                    options.modes));
        }
    }
    return ret;
};


replay.greenRedScale = function(p) {
    g = parseInt(255 * p);
    r = 255 - g;
    return 'rgb(' + r + ', ' + g + ', 100)';
};


replay.hex2rgb = function(hex) {
    return [
        parseInt(hex.substring(1, 3), 16),
        parseInt(hex.substring(3, 5), 16),
        parseInt(hex.substring(5, 7), 16),
    ];
};


replay.transformAsset = function(asset, options) {
    // Create a bare canvas of the correct dimensions
    asset = jaws.isDrawable(asset) ? asset : jaws.assets.data[asset];
    asset = jaws.isImage(asset) ? imageToCanvas(asset) : asset;
    var ret = document.createElement('canvas');
    ret.src = asset.src;
    ret.width = asset.width;
    ret.height = asset.height;
    var ctx = ret.getContext('2d');

    // Apply the transformations
    if (options.flipX) {
        ctx.translate(ret.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(asset, 0, 0);
    }

    return ret;
}


jaws.assets.loadTintedAsset = function(asset_name, tints) {
    // Create the tinted asset
    tints = jaws.isArray(tints) ? tints : [tints]
    var asset = this.data[asset_name]
    asset = jaws.isImage(asset) ? imageToCanvas(asset) : asset

    // Create a bare canvas of the correct dimensions with the base image
    var tinted_asset = document.createElement('canvas')
    tinted_asset.src = asset.src
    tinted_asset.width = asset.width / (tints.length + 1)
    tinted_asset.height = asset.height
    var tinted_ctx = tinted_asset.getContext('2d')
    tinted_ctx.drawImage(asset, 0, 0)

    // Apply each tinted mask in order
    for (var i = 0; i < tints.length; i++) {
        var canvas = document.createElement('canvas')
        canvas.width = asset.width / (tints.length + 1)
        canvas.height = asset.height;
        var ctx = canvas.getContext('2d')
        ctx.globalCompositeOperation = 'destination-atop'
        ctx.fillStyle = tints[i]
        ctx.fillRect(0, 0, tinted_asset.width, tinted_asset.height)
        ctx.drawImage(asset, -(i + 1) * tinted_asset.width, 0)
        tinted_ctx.drawImage(canvas, 0, 0);
    }

    // Store the new asset
    var tinted_name = asset_name + tints.join('')
    this.loaded[tinted_name] = true
    this.loading[tinted_name] = false
    this.data[tinted_name] = tinted_asset
}
