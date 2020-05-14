var clear = document.getElementById("yo").innerText;
if (clear == 'Industrial ' || clear == 'Financial ') {
    clear = clear.slice(0,-1) + 's';
}
var url = "/data/sector/" + clear;

// set the dimensions and margins of the graph
var margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#my_dataviz")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform",
        `${"translate(" + margin.left + "," + margin.top + ")"}`);

var parseTime = d3.timeParse("%Y-%m-%d");
//Read the data
d3.json(url).then(d => {
    d = d['points']
    d.forEach(function (da) {
        da['date'] = parseTime(da['date']);
        da['price'] = +da['price'];
    });
    console.log(d.sort((a,b) => {
        return new Date(a.date).getTime() - new Date(b.date).getTime();
    }));
    // Add X axis --> it is a date format
    var x = d3.scaleTime()
        .domain(d3.extent(d, function (a) {
            return a['date'];
        }))
        .range([0, width]);
    svg.append("g")
        .attr("transform", `${"translate(0," + height + ")"}`)
        .call(d3.axisBottom(x));
    // Add Y axis
    var y = d3.scaleLinear()
        .domain([0, d3.max(d, function (d) {
            return +d['price'];
        })])
        .range([height, 0]);
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add the line
    svg.append("path")
        .datum(d)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
            .x(function (d) {
                return x(d['date'])
            })
            .y(function (d) {
                return y(d['price'])
            })
        )
});
