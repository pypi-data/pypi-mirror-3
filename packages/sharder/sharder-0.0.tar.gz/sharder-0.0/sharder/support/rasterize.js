/*global WebPage, phantom, console, window */
(function() {

  var page = new WebPage(), config, address, output, size, timeoutID;
  
  var takeScreenshot;
  var pageShortcut = false;
  var expectTriggers = 1; // decrement when we see 'phantomjs screenshot' in log,
                          // take screenshot on 0
  var pageReady = false;

  if(phantom.args.length !== 1) {
    console.log('Usage: rasterize.js {url:"...", file:"..."}');
    phantom.exit(1);
  } else {                   
    config = JSON.parse(phantom.args[0]);

    // XXX phantomjs does not exit immediately for exceptions.
    window.setTimeout(function() {
      console.log('timeout!');
      phantom.exit(2);
    }, config.timeout || 16000);
    
    expectTriggers = config.triggers || 0;

    takeScreenshot = function() {
      page.render(output);
      phantom.exit(0);
    };

    address = config.url;
    output = config.file;
    if(address === undefined || output === undefined) {
      console.log('Bad arguments', phantom.args[0]);
      phantom.exit(1);
    }
    page.viewportSize = config.viewportSize;

    page.onConsoleMessage = function(msg) {
      if(msg == 'phantomjs screenshot') {
        console.log('ACK phantomjs screenshot');
        expectTriggers--;
        pageShortcut = (expectTriggers <= 0);
        if(pageReady && pageShortcut) {
          console.log('phantomjs screenshot in onConsoleMessage');
          takeScreenshot();
        }
      }
    };

    page.open(address, function(status) {
      if(status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit(2);
      } else {
        if(config.selector === '*') {
          // 'whole page' mode works with standalone svg, doesn't inject jQuery
          timeoutID = window.setTimeout(takeScreenshot, pageShortcut ? 0 : 8000);
          pageReady = true;
        } else {
          if(page.injectJs(config.jquery) === true) {
            var clipRect = page.evaluate(
              'function() {' +
                'var config = JSON.parse(\'' + JSON.stringify(config) + '\');' +
                'var el = jQuery(config.selector);' +
                'if(config.width) { el.width(config.width); }' +
                'if(config.height) { el.height(config.height); }' +
                'var offset = el.offset();' +
                'return {' +
                '  width: el.width(),' +
                '  height: el.height(),' +
                '  top: offset.top,' +
                '  left: offset.left' +
                '};' +
              '}'
            );
            page.clipRect = clipRect;
            // can we wait for complete render or script finish?
            timeoutID = window.setTimeout(takeScreenshot, pageShortcut ? 0 : 8000);
            pageReady = true;
          } else {
            console.log('Could not inject ' + config.jquery);
            phantom.exit(2);
          }
        }
      }
    });
  }
})();
