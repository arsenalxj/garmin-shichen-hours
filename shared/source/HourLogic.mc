using Toybox.Math;

// 所有时辰计算使用设备本地时间；数字时钟固定 24 小时制，不跟随系统设置。
module HourLogic {
    const BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
    const QUARTERS = ["初", "一", "二", "三", "四", "五", "六", "七"];
    const WEEKDAYS = ["日", "一", "二", "三", "四", "五", "六"];

    function hourIndex(hour) {
        return ((hour + 1) / 2).toNumber() % 12;
    }

    function quarterIndex(hour, minute) {
        return (((hour * 60 + minute + 60) % 120) / 15).toNumber();
    }

    function caption(hour, minute) {
        return BRANCHES[hourIndex(hour)] + "时 · " + QUARTERS[quarterIndex(hour, minute)] + "刻";
    }

    function timeText(hour, minute) {
        return hour.format("%02d") + ":" + minute.format("%02d");
    }

    function dateText(month, day, dayOfWeek) {
        return month.format("%02d") + "/" + day.format("%02d") + " 周" + WEEKDAYS[dayOfWeek - 1];
    }

    function validHeartRate(value) {
        return value != null && value > 0 && value != 255;
    }

    function freshHeartRate(value, sampleTime, now) {
        // 部分旧设备按分钟提供历史样本，五分钟内的有效值才作为最近心率。
        return validHeartRate(value) && sampleTime != null && sampleTime <= now && now - sampleTime <= 300;
    }

    function metricText(value) {
        return value == null || value < 0 ? "--" : value.toNumber().toString();
    }

    function batteryPercent(value) {
        var rounded = Math.round(value).toNumber();
        return rounded < 0 ? 0 : (rounded > 100 ? 100 : rounded);
    }

    function sleepBlanks(requiresBurnInProtection, sleeping) {
        return requiresBurnInProtection && sleeping;
    }
}
