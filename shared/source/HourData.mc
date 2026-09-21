using Toybox.Activity;
using Toybox.ActivityMonitor;
using Toybox.System;
using Toybox.Time;
using Toybox.Time.Gregorian;

class HourData {
    var hour = 0;
    var minute = 0;
    var month = 1;
    var day = 1;
    var dayOfWeek = 1;
    var is24Hour = true;
    var battery = 0;
    var steps = null;
    var heartRate = null;
    var requiresBurnInProtection = false;

    function initialize() {}

    function update(withMetrics) {
        var now = Time.now();
        var info = Gregorian.info(now, Time.FORMAT_SHORT);
        hour = info.hour;
        minute = info.min;
        month = info.month;
        day = info.day;
        dayOfWeek = info.day_of_week;
        var settings = System.getDeviceSettings();
        is24Hour = settings.is24Hour;
        if (settings has :requiresBurnInProtection) {
            requiresBurnInProtection = settings.requiresBurnInProtection;
        }
        if (!withMetrics) { return; }
        battery = HourLogic.batteryPercent(System.getSystemStats().battery);
        steps = ActivityMonitor.getInfo().steps;
        heartRate = readHeartRate(now.value());
    }

    function readHeartRate(now) {
        var current = Activity.getActivityInfo().currentHeartRate;
        if (HourLogic.validHeartRate(current)) { return current; }
        if (ActivityMonitor has :getHeartRateHistory) {
            var iterator = ActivityMonitor.getHeartRateHistory(1, true);
            var sample = iterator.next();
            if (sample != null && sample.when != null &&
                HourLogic.freshHeartRate(sample.heartRate, sample.when.value(), now)) {
                return sample.heartRate;
            }
        }
        return null;
    }
}
