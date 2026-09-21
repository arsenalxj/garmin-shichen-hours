using Toybox.Test;

(:test)
function allMinutes(logger) {
    // 以 23:00 为起点完整走过一天，独立计数每时辰八刻。
    for (var elapsed = 0; elapsed < 1440; elapsed += 1) {
        var clockMinute = (1380 + elapsed) % 1440;
        var hour = (clockMinute / 60).toNumber();
        var minute = clockMinute % 60;
        Test.assertEqual(HourLogic.hourIndex(hour), (elapsed / 120).toNumber());
        Test.assertEqual(HourLogic.quarterIndex(hour, minute), ((elapsed % 120) / 15).toNumber());
    }
    return true;
}

(:test)
function midnightBoundaries(logger) {
    Test.assertEqual(HourLogic.caption(22, 59), "亥时 · 七刻");
    Test.assertEqual(HourLogic.caption(23, 0), "子时 · 初刻");
    Test.assertEqual(HourLogic.caption(23, 14), "子时 · 初刻");
    Test.assertEqual(HourLogic.caption(23, 15), "子时 · 一刻");
    Test.assertEqual(HourLogic.caption(23, 44), "子时 · 二刻");
    Test.assertEqual(HourLogic.caption(23, 45), "子时 · 三刻");
    Test.assertEqual(HourLogic.caption(23, 59), "子时 · 三刻");
    Test.assertEqual(HourLogic.caption(0, 0), "子时 · 四刻");
    Test.assertEqual(HourLogic.caption(0, 59), "子时 · 七刻");
    Test.assertEqual(HourLogic.caption(1, 0), "丑时 · 初刻");
    return true;
}

(:test)
function displayFormats(logger) {
    Test.assertEqual(HourLogic.timeText(0, 3, true), "00:03");
    Test.assertEqual(HourLogic.timeText(0, 3, false), "12:03");
    Test.assertEqual(HourLogic.timeText(12, 0, false), "12:00");
    Test.assertEqual(HourLogic.timeText(23, 59, false), "11:59");
    Test.assertEqual(HourLogic.periodText(0), "上午");
    Test.assertEqual(HourLogic.periodText(12), "下午");
    Test.assertEqual(HourLogic.dateText(9, 21, 2), "09/21 周一");
    Test.assertEqual(HourLogic.dateText(12, 31, 1), "12/31 周日");
    return true;
}

(:test)
function missingAndStaleMetrics(logger) {
    Test.assert(!HourLogic.validHeartRate(null));
    Test.assert(!HourLogic.validHeartRate(0));
    Test.assert(!HourLogic.validHeartRate(-1));
    Test.assert(!HourLogic.validHeartRate(255));
    Test.assert(HourLogic.freshHeartRate(72, 700, 1000));
    Test.assert(!HourLogic.freshHeartRate(72, 699, 1000));
    Test.assert(!HourLogic.freshHeartRate(72, 1001, 1000));
    Test.assert(!HourLogic.freshHeartRate(72, null, 1000));
    Test.assertEqual(HourLogic.metricText(null), "--");
    Test.assertEqual(HourLogic.metricText(0), "0");
    Test.assertEqual(HourLogic.metricText(99999), "99999");
    Test.assertEqual(HourLogic.metricText(123), "123");
    Test.assertEqual(HourLogic.batteryPercent(99.6), 100);
    Test.assertEqual(HourLogic.batteryPercent(-1), 0);
    Test.assertEqual(HourLogic.batteryPercent(101), 100);
    return true;
}

(:test)
function sleepAndWake(logger) {
    Test.assert(HourLogic.sleepBlanks(true, true));
    Test.assert(!HourLogic.sleepBlanks(true, false));
    Test.assert(!HourLogic.sleepBlanks(false, true));
    Test.assert(!HourLogic.sleepBlanks(false, false));
    return true;
}

(:test)
function deviceDataSmoke(logger) {
    // 在真正的设备 API 环境读取一次，再走省电读取路径，捕获旧机型 API 差异。
    var data = new HourData();
    data.update(true);
    Test.assert(data.hour >= 0 && data.hour < 24);
    Test.assert(data.minute >= 0 && data.minute < 60);
    Test.assert(data.month >= 1 && data.month <= 12);
    Test.assert(data.day >= 1 && data.day <= 31);
    Test.assert(data.dayOfWeek >= 1 && data.dayOfWeek <= 7);
    Test.assert(data.battery >= 0 && data.battery <= 100);
    Test.assert(data.heartRate == null || HourLogic.validHeartRate(data.heartRate));
    logger.debug("requiresBurnInProtection=" + data.requiresBurnInProtection.toString());
    data.update(false);
    return true;
}
