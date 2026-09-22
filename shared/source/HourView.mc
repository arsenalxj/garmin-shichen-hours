using Toybox.Graphics;
using Toybox.Lang;
using Toybox.Math;
using Toybox.WatchUi;

class HourView extends WatchUi.WatchFace {
    var _data as HourData;
    var _sleeping = false;
    var _scale = 1.0;
    var _cx = 0;
    var _fonts as Lang.Array<Graphics.FontType> = [];
    var _polygon as Lang.Array<Lang.Array<Lang.Number>>;

    function initialize() {
        WatchFace.initialize();
        _data = new HourData();
        // 30° 扇环，每边 12 段；重用顶点数组，避免每帧制造大量小对象。
        _polygon = [];
        for (var i = 0; i < 26; i += 1) { _polygon.add([0, 0]); }
    }

    function onLayout(dc) {
        _scale = dc.getWidth() / 466.0;
        _cx = dc.getWidth() / 2;
        _fonts = [
            WatchUi.loadResource(Rez.Fonts.Ring),
            WatchUi.loadResource(Rez.Fonts.RingActive),
            WatchUi.loadResource(Rez.Fonts.Caption),
            WatchUi.loadResource(Rez.Fonts.Date),
            WatchUi.loadResource(Rez.Fonts.Time),
            WatchUi.loadResource(Rez.Fonts.TimeSleep),
            WatchUi.loadResource(Rez.Fonts.Metric)
        ];
    }

    function onEnterSleep() { _sleeping = true; }
    function onExitSleep() { _sleeping = false; WatchUi.requestUpdate(); }

    function onUpdate(dc) {
        _data.update(!_sleeping);
        render(dc, _data, _sleeping);
    }

    function px(value) { return Math.round(value * _scale).toNumber(); }

    function lineWidth(value) {
        var width = px(value);
        return width < 1 ? 1 : width;
    }

    function color(value, sleeping) {
        if (!sleeping || Theme.DIM == 1.0) { return value; }
        var r = Math.round(((value >> 16) & 255) * Theme.DIM).toNumber();
        var g = Math.round(((value >> 8) & 255) * Theme.DIM).toNumber();
        var b = Math.round((value & 255) * Theme.DIM).toNumber();
        return (r << 16) | (g << 8) | b;
    }

    function text(dc, x, baseline, fontIndex, value, ink, alignment) {
        var base = FontMetrics.BASES[fontIndex];
        if (Theme.SERIF && (fontIndex == 4 || fontIndex == 5)) {
            base = FontMetrics.SERIF_BASES[fontIndex - 4];
        }
        dc.setColor(ink, Graphics.COLOR_TRANSPARENT);
        dc.drawText(px(x), px(baseline) - base, _fonts[fontIndex], value, alignment);
    }

    function sector(dc, index, active, outline) {
        var inner = active ? 158.0 : 174.0;
        var a0 = -90.0 + index * 30 - 15 + 1.1;
        var span = 30.0 - 2.2;
        for (var j = 0; j <= 12; j += 1) {
            var angle = (a0 + span * j / 12.0) * Math.PI / 180.0;
            var cos = Math.cos(angle);
            var sin = Math.sin(angle);
            _polygon[j][0] = _cx + px(230 * cos);
            _polygon[j][1] = _cx + px(230 * sin);
            _polygon[25 - j][0] = _cx + px(inner * cos);
            _polygon[25 - j][1] = _cx + px(inner * sin);
        }
        if (outline) {
            dc.setPenWidth(lineWidth(3));
            for (var k = 0; k < 26; k += 1) {
                var next = (k + 1) % 26;
                dc.drawLine(_polygon[k][0], _polygon[k][1], _polygon[next][0], _polygon[next][1]);
            }
            dc.setPenWidth(1);
        } else {
            dc.fillPolygon(_polygon);
        }
    }

    function render(dc, data, sleeping) {
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();
        if (HourLogic.sleepBlanks(data.requiresBurnInProtection, sleeping)) { return; }
        if (dc has :setAntiAlias) { dc.setAntiAlias(true); }
        var face = color(sleeping ? Theme.AOD_FACE : Theme.FACE, sleeping);
        dc.setColor(face, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(_cx, _cx, px(230));
        if (Theme.RIM_ON && !sleeping) {
            dc.setColor(Theme.RIM_BLEND, Graphics.COLOR_TRANSPARENT);
            dc.setPenWidth(lineWidth(2));
            dc.drawCircle(_cx, _cx, px(228.5));
            dc.setPenWidth(1);
        }
        var current = HourLogic.hourIndex(data.hour);
        for (var i = 0; i < 12; i += 1) {
            var active = i == current;
            var fill = Theme.CYCLE ? Theme.HOUR_COLORS[i] : (active ? Theme.CURRENT : Theme.SEGMENT);
            dc.setColor(color(fill, sleeping), Graphics.COLOR_TRANSPARENT);
            if (!sleeping || active) { sector(dc, i, active, sleeping); }
            var ink;
            if (Theme.CYCLE) {
                ink = sleeping ? color(Theme.HOUR_COLORS[i], true) : Theme.HOUR_INKS[i];
            } else {
                ink = color(active ? (sleeping ? Theme.CURRENT : Theme.CURRENT_TEXT) : Theme.SEGMENT_TEXT, sleeping);
            }
            var angle = (-90 + i * 30) * Math.PI / 180.0;
            text(dc, 233 + 202 * Math.cos(angle), 244 + 202 * Math.sin(angle),
                active ? 1 : 0, HourLogic.BRANCHES[i], ink, Graphics.TEXT_JUSTIFY_CENTER);
        }
        var accent = color(Theme.CYCLE ? Theme.HOUR_COLORS[current] : Theme.CURRENT, sleeping);
        var colTime = color(sleeping ? Theme.AOD_TIME : Theme.TIME, sleeping);
        var colDate = color(sleeping ? Theme.AOD_DATE : Theme.DATE, sleeping);
        var colMeta = color(sleeping ? Theme.AOD_META : Theme.META, sleeping);
        // 中央各行基线按真实字形墨迹排：小注 131 / 日期 170 / 时间 268 / 强调线 281 / 数据 328
        text(dc, 233, 131, 2, HourLogic.caption(data.hour, data.minute), accent, Graphics.TEXT_JUSTIFY_CENTER);
        text(dc, 233, 170, 3, HourLogic.dateText(data.month, data.day, data.dayOfWeek), colDate, Graphics.TEXT_JUSTIFY_CENTER);
        text(dc, 233, 268, sleeping ? 5 : 4, HourLogic.timeText(data.hour, data.minute), colTime, Graphics.TEXT_JUSTIFY_CENTER);
        if (!sleeping) {
            dc.setColor(accent, Graphics.COLOR_TRANSPARENT);
            dc.fillRectangle(px(209), px(281), px(48), lineWidth(4));
            // 数据区一行「电量 ｜ 步数 ｜ 心跳」，锚点与原型一致（文字端 ±76、分隔线 ±60）
            var batteryInk = data.battery <= 20 ? 0xD92121 : colMeta;
            text(dc, 157, 328, 6, data.battery.toString(), batteryInk, Graphics.TEXT_JUSTIFY_RIGHT);
            text(dc, 173, 328, 6, "｜", colMeta, Graphics.TEXT_JUSTIFY_CENTER);
            text(dc, 233, 328, 6, HourLogic.metricText(data.steps), colMeta, Graphics.TEXT_JUSTIFY_CENTER);
            text(dc, 293, 328, 6, "｜", colMeta, Graphics.TEXT_JUSTIFY_CENTER);
            text(dc, 309, 328, 6, HourLogic.metricText(data.heartRate), colMeta, Graphics.TEXT_JUSTIFY_LEFT);
        }
    }
}
