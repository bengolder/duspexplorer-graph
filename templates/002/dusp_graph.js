// helper functions
function getNeighborNodes(node){
    var id = node.id;
    var neighbors = graph[id];
    var selector = '#' + neighbors.join(',#');
    return selector;
}

function getDocumentSize(){
    var w = $(document).width();
    var h = $(document).height();
    return [w, h];
}

function getCenter(obj){
    var w = obj.width();
    var h = obj.height();
    var offset = obj.offset();
    var x = offset.left + (w / 2);
    var y = offset.top + (h / 2);
    return {'x':x, 'y':y};
}

function getCenters(neighbors){
    var centers = [];
    $(neighbors).each(function(i, elem){
        obj = $(elem);
        var center = getCenter(obj);
        centers.push(center);
    });
    return centers;
}


function drawLines (target, g, neighborclass) {
    var thisCenter = getCenter($(target));
    var neighbors = getNeighborNodes(target);
    $(neighbors).addClass(neighborclass);
    var centers = getCenters(neighbors);
    var lines = g.selectAll("line")
        .data(centers).enter().append("line");

    lines.attr('x1', thisCenter.x)
        .attr('y1', thisCenter.y)
        .attr('x2', function(d){ return d.x })
        .attr('y2', function(d){ return d.y });

    var gclass = g[0][0].className.baseVal;

    if (gclass == "hoverlines"){
        lines.attr('stroke-dasharray', '8, 4');
    }
}

function removeLines (target, g, neighborclass) {
    var neighbors = getNeighborNodes(target);
    $(neighbors).removeClass(neighborclass);
    g.selectAll("line")
        .data([]).exit().remove();
}

var svg = d3.select("#geom_background").append("svg")
    .attr("width", getDocumentSize()[0])
    .attr("height", getDocumentSize()[1]);

var hovers = svg.append("g").attr("class", "hoverlines");

var lines = svg.selectAll("line");

// listeners
$('body').on('mouseover','.node', function(e){

    $(this).addClass('targeted')
        .addClass('hovered');
    drawLines(this, hovers, 'highlighted');

}).on('mouseout', '.node', function(e){

    var target = $(this);
    removeLines(this, hovers, 'highlighted');
    target.removeClass('targeted');
    target.removeClass('hovered');

}).on('click', '.node', function(e){

    var target = $(this);

    if (target.hasClass('selected')) {
        target.removeClass('selected');
        $('.'+this.id).remove();
        var neighbors = getNeighborNodes(this);
        $(neighbors).removeClass('highlight-stay');
    } else {
        target.addClass('selected');
        var svgLayer = svg.append("g").attr("class", 
            "select " + this.id);
        drawLines(this, svgLayer, 'highlight-stay');
    }

});





