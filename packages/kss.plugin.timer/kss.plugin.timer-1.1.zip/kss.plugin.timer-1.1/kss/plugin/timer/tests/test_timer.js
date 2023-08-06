var global = this;
global.window = {setInterval: function(f, i) {global.interval = [f, i];}}
global.kukit = {eventsGlobalRegistry: {registerForAllEvents: function() {}}};

load('../javascript/kss_timer.js');

function fakedisplayel() {
    this.__defineGetter__('innerHTML', function() {
        return this._innerHTML;
    });
    this.__defineSetter__('innerHTML', function(h) {
        this._innerHTML = h;
    });
};

function setup() {
    var del = global.displayel = new fakedisplayel();
    global.currsecs = null;
    var t = global.timer =
        new kukit.timer.Timer('%0M:%0S', '%h:%0M:%0S', [del]);
    t.onupdate = function(a) {global.currsecs = a.defaultParameters.seconds};
};

function test_timer_functional_init() {
    timer.start();
    timer.update();
    testing.assertEquals(global.currsecs, 0);
    testing.assertEquals(displayel.innerHTML, '00:00');
};

function test_timer_functional_seconds() {
    timer._starttime = (new Date()).getTime() - 1000;
    timer.update();
    testing.assert(global.currsecs > 0);
    testing.assert(global.currsecs < 3);
    testing.assert(displayel.innerHTML == '00:01' ||
                   displayel.innerHTML == '00:02');
};

function test_timer_functional_minute() {
    timer._starttime = (new Date()).getTime() - 60000;
    timer.update();
    testing.assert(global.currsecs > 59);
    testing.assert(global.currsecs < 62);
    testing.assert(displayel.innerHTML == '01:00' ||
                   displayel.innerHTML == '01:01');
};

function test_timer_functional_hours() {
    timer._starttime = (new Date()).getTime() - 3600000;
    timer.update();
    testing.assert(global.currsecs == 3600 ||
                   global.currsecs == 3601);
    testing.assert(displayel.innerHTML == '1:00:00' ||
                   displayel.innerHTML == '1:00:01');
};

function test_timerstart() {
    timer.startvalue = 3600;
    timer._settings_changed();
    testing.assert(global.currsecs == 3600 || global.currsecs == 3601);
};
