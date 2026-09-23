using Toybox.Graphics;
using Toybox.System;
using Toybox.Test;

(:test)
function fr255RasterTransitions(logger) {
    if (!RasterAssets.ENABLED) { return true; }
    if (!(Graphics has :createBufferedBitmap)) { return false; }
    var buffer = Graphics.createBufferedBitmap({:width => 260, :height => 260});
    var bitmap = buffer.get();
    var dc = bitmap.getDc();
    var view = new HourView();
    view.onLayout(dc);
    var data = new HourData();
    data.month = 12;
    data.day = 31;
    data.dayOfWeek = 7;
    data.requiresBurnInProtection = false;
    var peak = 0;
    for (var i = 0; i < 12; i += 1) {
        data.hour = (i * 2 + 23) % 24;
        data.minute = (i % 4) * 15;
        data.battery = i % 2 == 0 ? 19 : 100;
        data.steps = i % 3 == 0 ? null : 99999;
        data.heartRate = i % 3 == 0 ? null : 199;
        // 每个时辰都经历正常→省电→唤醒，覆盖切换后的资源释放与重新加载。
        view.render(dc, data, false);
        view.render(dc, data, true);
        view.render(dc, data, false);
        Test.assertEqual(view._fonts.size(), 0);
        var used = System.getSystemStats().usedMemory;
        if (used > peak) { peak = used; }
    }
    Test.assert(peak < 114688);
    logger.debug("FR255 raster peak VM bytes=" + peak);
    return true;
}
