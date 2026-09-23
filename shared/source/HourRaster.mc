using Toybox.Graphics;
using Toybox.Lang;
using Toybox.WatchUi;

// 字形边缘已与该主题的真实背景混合，设备只需复制像素。
class HourRaster {
    var _mode = -1;
    var _hour = -1;
    var _face = null;
    var _patch = null;
    var _ids as Lang.Array = [null, null, null, null, null, null, null];
    var _atlases as Lang.Array = [null, null, null, null, null, null, null];

    function initialize() {}

    function begin(dc, current, sleeping) {
        if (!RasterAssets.ENABLED || !(dc has :drawBitmap2)) { return false; }
        var mode = sleeping ? 1 : 0;
        if (_mode != mode) {
            _face = null;
            _patch = null;
            for (var i = 0; i < 7; i += 1) { _ids[i] = null; _atlases[i] = null; }
            _face = WatchUi.loadResource(RasterAssets.FACES[mode]);
            _mode = mode;
            _hour = -1;
        }
        var patch = RasterAssets.PATCHES[mode][current];
        if (_hour != current) {
            _patch = null;
            _patch = WatchUi.loadResource(patch[0]);
            _hour = current;
        }
        dc.drawBitmap(0, 0, _face);
        dc.drawBitmap(patch[1], patch[2], _patch);
        return true;
    }

    function text(dc, x, baseline, index, value, ink, alignment) {
        if (!RasterAssets.ENABLED || _mode < 0 || !(dc has :drawBitmap2)) { return false; }
        var variants = RasterAssets.ATLASES[_mode][index] as Lang.Array<Lang.Array>;
        var resource = null;
        for (var i = 0; i < variants.size(); i += 1) {
            if (variants[i][0] == ink) { resource = variants[i][1]; break; }
        }
        if (resource == null) { return false; }
        if (_ids[index] != resource) {
            _atlases[index] = null;
            _atlases[index] = WatchUi.loadResource(resource);
            _ids[index] = resource;
        }
        var spec = RasterAssets.FONTS[index] as Lang.Array;
        var glyphs = spec[1] as Lang.Dictionary<Lang.Number, Lang.Array<Lang.Number>>;
        var chars = value.toCharArray() as Lang.Array<Lang.Char>;
        var width = 0;
        // 先校验整串，避免出现半串位图、半串回退字体。
        for (var i = 0; i < chars.size(); i += 1) {
            var glyph = glyphs[chars[i].toNumber()];
            if (glyph == null) { return false; }
            width += glyph[6];
        }
        var pen = x;
        if (alignment == Graphics.TEXT_JUSTIFY_CENTER) { pen -= (width + 1) / 2; }
        else if (alignment == Graphics.TEXT_JUSTIFY_RIGHT) { pen -= width; }
        var top = baseline - spec[0];
        for (var i = 0; i < chars.size(); i += 1) {
            var glyph = glyphs[chars[i].toNumber()];
            // drawBitmap2 的裁剪区域保留原图坐标；抵消图集位置后才是字形的目标锚点。
            dc.drawBitmap2(pen + glyph[4] - glyph[0], top + glyph[5] - glyph[1], _atlases[index], {
                :bitmapX => glyph[0], :bitmapY => glyph[1],
                :bitmapWidth => glyph[2], :bitmapHeight => glyph[3]
            });
            pen += glyph[6];
        }
        return true;
    }
}
