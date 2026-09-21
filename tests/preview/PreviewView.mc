// 仅由 scripts/preview.py 编译，商店/正式构建从不包含此目录。
class PreviewView extends HourView {
    function initialize() { HourView.initialize(); }

    function onUpdate(dc) {
        _data.hour = PreviewScenario.HOUR;
        _data.minute = PreviewScenario.MINUTE;
        _data.month = 9;
        _data.day = PreviewScenario.DAY;
        _data.dayOfWeek = PreviewScenario.WEEKDAY;
        _data.is24Hour = PreviewScenario.IS_24;
        _data.battery = PreviewScenario.BATTERY;
        _data.steps = PreviewScenario.STEPS;
        _data.heartRate = PreviewScenario.HR;
        _data.requiresBurnInProtection = PreviewScenario.PROTECTED;
        render(dc, _data, PreviewScenario.SLEEPING);
    }
}
