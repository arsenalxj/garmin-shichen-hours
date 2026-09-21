using Toybox.Application;

class HourApp extends Application.AppBase {
    function initialize() { AppBase.initialize(); }
    (:production)
    function getInitialView() { return [new HourView()]; }

    (:preview)
    function getInitialView() { return [new PreviewView()]; }
}
