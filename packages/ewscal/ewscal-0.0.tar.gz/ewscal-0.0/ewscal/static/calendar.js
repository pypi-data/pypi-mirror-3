var calendar = function(data) {
    var fg = "black";
    var bg = "#fff";
    var i;
    for(i=0; i<data.events.length; i++) {
      data.events[i].start = new Date(Date.parse(data.events[i].start));
      data.events[i].end = new Date(Date.parse(data.events[i].end));
    }

    var widthMargin = 40;
    var heightMargin = 40;

    var roomLabelWidth = 165;

    var parentEl = document.getElementById('calendar');
    var fullWidth = parentEl.offsetWidth;
    var fullHeight = parentEl.offsetHeight;

    var w = fullWidth - widthMargin,
        h = fullHeight - heightMargin;

    var start = d3.time.hour(new Date());
    var end = new Date(start.getTime() + 1000*60*60*Math.floor(fullWidth/160));

    var x = d3.time.scale().domain([start, end]).range([0, w]),
        y = d3.scale.ordinal().domain(data.names).rangeBands([0, h], .2);

    var fontSize = Math.floor(y.rangeBand() * 3/4);

    var svg = d3.select(parentEl)
      .append("svg:svg")
      .attr("width", fullWidth)
      .attr("height", fullHeight);

    var defs = svg.append('svg:defs');

    var gradientWidth = 10;

    defs.append('svg:linearGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', -gradientWidth).attr('y1', 0).attr('x2', 0).attr('y2', 0)
      .attr('id', 'master').call(
          function(gradient) {
            gradient.append('svg:stop')
              .attr('offset', '0%').attr('style', 'stop-color:#fff;stop-opacity:1');
            gradient.append('svg:stop')
              .attr('offset', '100%').attr('style', 'stop-color:#fff;stop-opacity:0');
          });

    defs.append('svg:linearGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', 0).attr('x2', 5).attr('y2', 0)
      .attr('id', 'roomNames').call(
          function(gradient) {
            gradient.append('svg:stop')
              .attr('offset', '0%').attr('style', 'stop-color:'+bg+';stop-opacity:0');
            gradient.append('svg:stop')
              .attr('offset', '100%').attr('style', 'stop-color:'+bg+';stop-opacity:1');
          });

    var vis = svg.append("svg:g")
      .attr("transform", "translate(" + 30 + ",0)"); // leave space for the first tick e.g. '11 AM'

    defs.selectAll('.gradient').data(data.events, function(d) { return d.id; })
      .enter().append('svg:linearGradient')
      .attr('id', function(d, i) { return 'gradient' + i; })
      .attr('class', 'gradient')
      .attr('xlink:href', '#master')
      .attr('gradientTransform', function(d) { 
          var width = (x(d.end) - x(d.start)) - 5;
          if (width === NaN) {
            // width = 0;
          }
          return 'translate(' + width + ')'; 
      });

    var bars = vis.selectAll("g.bar")
      .data(data.events, function(d) { return d.id; })
      .enter().append("svg:g")
      .attr("class", "bar")
      .attr("transform", function(d) { return "translate(" + x(d.start) + ',' + y(d.user) + ")"; })
      .attr("opacity", function(d) { 
          if(d.busy === 'Free') {
          return 0;
          }
          return 1;
          });

    bars.append("svg:rect")
      .attr("fill", "#4682b4")
      .attr("rx", "5")
      .attr("ry", "15")
      .attr("width", function(d) { 
          return x(d.end) - x(d.start);
          }).attr("height", y.rangeBand());

    bars.append("svg:text")
      .attr("x", ".5em")
      .attr("y", y.rangeBand()/2)
      .attr("dy", ".35em")
      .attr("fill", function(d, i) { return "url(#gradient" + i + ")"; } )
      .attr("font-size", fontSize)
      .attr("text-anchor", "start")
      .text(function(d) { return d.subject; });

    var rules = vis.selectAll("g.rule")
      .data(x.ticks(10))
      .enter().append("svg:g")
      .attr("class", "rule")
      .attr("transform", function(d) { return "translate(" + x(d) + ",0)"; });

    rules.append("svg:line")
      .attr("y1", h)
      .attr("y2", h + 6)
      .attr("stroke", fg);

    rules.append("svg:line")
      .attr("y1", 0)
      .attr("y2", h)
      .attr("stroke", "white")
      .attr("stroke-opacity", .3);

    rules.append("svg:text")
      .attr("y", h + 9)
      .attr("dy", ".71em")
      .attr("text-anchor", "middle")
      .attr("fill", fg)
      .text(x.tickFormat(10));

    vis.append("svg:rect")
      .attr("width", roomLabelWidth + widthMargin)
      .attr("height", h)
      .attr("fill", "url(#roomNames)")
      .attr("transform", "translate(" + (w-roomLabelWidth) + ")");

    var rooms = vis.selectAll("g.room")
      .data(data.names)
      .enter().append('svg:g')
      .attr("class", "room")
      .append("svg:text")
      .attr("fill", fg)
      .attr("text-anchor", "end")
      .attr("dy", ".35em")
      .attr("transform", function(d) { 
          return "translate(" + w + "," + (y(d) + y.rangeBand() / 2) + ")"; 
          }).text(function (d) { return data.displaynames[d]; });

    var xNow = x(new Date());
    vis.append("svg:line")
      .attr("x1", xNow)
      .attr("x2", xNow)
      .attr("y1", 0)
      .attr("y2", h)
      .attr("stroke", fg)
      .attr("stroke-opacity", "0.25")
      .attr("stroke-width", "4")
      .attr("shape-rendering", "crispEdges");

    // left margin
    svg.append("svg:rect")
      .attr("width", 20)
      .attr("height", h)
      .attr("fill", bg)
      .attr("x", 0);

    // Done!
    console.log('phantomjs screenshot');
};

