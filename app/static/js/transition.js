let selector = document.getElementById('selector');
let resume_btn = document.getElementById('resume');
let pause_btn = document.getElementById('pause');
let slider = document.getElementById('slider');

let map_url = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-10m.json';
let width = 1000;
let height = 500;
let date, timer, center, range;
let height_only = ['United States of America', 'France', 'Russia', 'Fiji'];
let mode = 'Cases';

let get_date = () => {
    return date.toISOString().slice(0, 10);
};
let get_date_formatted = () => {
    return date.toLocaleString('default', {month: 'long', day: 'numeric', year: "numeric"});
}

let path = d3.geoPath(d3.geoEqualEarth()
    .scale(width / 2 / Math.PI)
    .center([0, 0])
    .translate([width / 2, height / 2]));

let data_full = d3.json('/data/cases').then(d => {
    data_full = d;
    $('.selectpicker').prop('disabled', false);
    $('.selectpicker').selectpicker('refresh');
    range = Object.keys(data_full).length;
    slider.setAttribute('max', range);
    slider.removeAttribute('disabled');
    mode = 'Cases';
    render(data_full);
});
let data_deaths = d3.json('/data/deaths');
let data_recovered = d3.json('/data/recoveries');

let map_data = d3.json(map_url)
let get_percent = (d, data) => {
    let data_dated = data[get_date()];
    if (data_dated.hasOwnProperty(d.properties.name)) {
        return data_dated[d.properties.name][0];
    } else return undefined;
};
let get_cases = (d) => {
    let data_dated = data_full[get_date()];
    if (data_dated !== undefined && data_dated.hasOwnProperty(d.properties.name)) {
        return data_dated[d.properties.name][1].toLocaleString();
    } else return '<i>unknown</i>';
};

let color = d3.scaleSequential()
    .domain([0, 0.005])
    .interpolator(d3.interpolateRgbBasis(['#cccccd', 'red', 'firebrick']))
    .unknown('#ccc');

let highlight =  function() {
    let element = d3.select(this);
    if (element.attr('stroke') != '#000001'){
        d3.select(this)
        .attr('stroke', 'black')
        .attr('vector-effect', 'non-scaling-stroke');
    }
};

let format_tooltip = (d) => {
    return `<b>${d.properties.name}</b><br>${mode}: ${get_cases(d)}`
};

let display_tooltip = (d) => {
    if (center != d.properties.name) {
        $('#tooltip').css({top: d3.event.pageY, left: d3.event.pageX});
        d3.select('.tooltip').style('pointer-events', 'none');
        d3.select('#tooltip').attr('data-original-title', format_tooltip(d));
        $('[data-toggle="tooltip"]').tooltip('show');
    }
};

let hide_tooltip = function(d) {
    $('[data-toggle="tooltip"]').tooltip('hide');
    if (center != d.properties.name){
        d3.select(this).attr('stroke', null);
    }
};

let ramp_vertical = (color, n = 256) => {
    let canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = n;
    const context = canvas.getContext("2d");
    for (let i = 0; i < n; ++i) {
        context.fillStyle = color(i / (n - 1));
        context.fillRect(0, i, 1, 1);
    }
    return canvas;
};

let ramp_horizontal = (color, n = 256) => {
    let canvas = document.createElement('canvas');
    canvas.width = n;
    canvas.height = 1;
    const context = canvas.getContext("2d");
    for (let i = 0; i < n; ++i) {
        context.fillStyle = color(i / (n - 1));
        context.fillRect(i, 0, 1, 1);
    }
    return canvas;
};

let popover = (country, d) => {
    $('[data-toggle="tooltip"]').tooltip('hide');

    if (country.attr('class') != null) {
        d3.json(`/data/${d.properties.name}`).then(datum => {
            d3.select('#popover').datum(datum)
                .attr('data-toggle', 'popover')
                .attr('data-placement', 'right')
                .attr('title', d.properties.name)
                .attr('data-content', () => {
                    let index = Math.floor((date - new Date('2020-01-22'))/(1000*60*60*24));
                    return `<b>Population (2018)</b>: ${datum['population'].toLocaleString()}`
                        + '<br><b>Cases:</b> '
                        + `<span id="pop-c">${datum['cases'][index].toLocaleString()}</span>`
                        + '<br><b id>Deaths:</b> '
                        + `<span id="pop-d">${datum['deaths'][index].toLocaleString()}</span>`
                        + '<br><b>Recoveries:</b> '
                        + `<span id="pop-r">${datum['recoveries'][index].toLocaleString()}</span>` + '<hr>';
                });
            $(`[title="${d.properties.name}"]`).popover('show');

            let body = d3.select('.popover-body');
            body.append('div')
                .style('text-align', 'center')
                .style('margin-bottom', '2vh')
                .append('b').text('Total');
            let total_graphs = body.append('svg')
                .attr('width', 250)
                .attr('height', 60);
            body.append('hr');
            body.append('div')
                .style('text-align', 'center')
                .style('margin-bottom', '2vh')
                .append('b').text('New');
            let new_graphs = body.append('svg')
                .attr('width', 250)
                .attr('height', 60);
            body.append('hr');
            body.append('div')
                .style('text-align', 'center')
                .style('margin-bottom', '1vh')
                .append('b').text('Doubling Rate');
            let growth = body.append('svg')
                .attr('width', 250)
                .attr('height', 60);

            let pairwise_diff = (prev => val => {
                let diff = Math.abs(val-prev);
                prev = val;
                return diff;
            });
            let draw_graph = (svg, data, fill_color, adjustment) => {
                let y = d3.scaleLinear().domain([0, d3.max(data)]).range([0, 50]);
                let graph = svg.append('g');
                graph.attr('fill', fill_color)
                    .selectAll('rect').data(data).join('rect')
                    .attr("x", (d, i) => i * 80 / range)
                    .attr("width", 80 / range)
                    .attr('y', d => 50 - y(d))
                    .attr('height', d => y(d))
                    .attr('transform', `translate(${adjustment},5)`);
                graph.append('text')
                    .text(d3.max(data))
                    .attr('x', 0)
                    .attr('y', 0)
                    .attr('fill', 'black')
                    .attr('text-anchor', 'start')
                    .attr('transform', `translate(${adjustment+5},10)`)
                    .style('font', '10px bold');
            };
            let check = (dataset, fill_color, adjustment = 0) => {
                let data = datum[dataset]
                if(d3.max(data) != 0) {
                    draw_graph(total_graphs, data, fill_color, adjustment);
                    draw_graph(new_graphs, data.map(pairwise_diff(0)), fill_color, adjustment);
                }
            }

            check('cases', 'red');
            check('deaths', 'purple', 80);
            check('recoveries', 'blue', 160);

            let scale = d3.scaleSequential()
                .domain([3, 30])
                .interpolator(d3.interpolateRgbBasis(['#f60', '#f4e5d2']))
                .unknown('#ccc');

            let new_cases = datum['cases'].map(pairwise_diff(0));
            let growth_rates =  datum['cases'].map((v,i) => v / new_cases[i]);
            growth.append('g').selectAll('rect').data(growth_rates).join('rect')
                .attr("x", (d, i) => i * 250 / range)
                .attr("width", 250 / range)
                .attr('y', 0)
                .attr('height', 30)
                .attr('fill', d => scale(d));
            growth.append('image')
                .attr('y', 35)
                .attr('width', 250)
                .attr('height', 5)
                .attr('preserveAspectRatio', 'none')
                .attr('transform', 'rotate(180,125,40)')
                .attr('xlink:href', ramp_horizontal(scale.interpolator()).toDataURL());
            growth.append('text')
                .text('>30 Days')
                .attr('x', 0)
                .attr('y', 55)
                .attr('fill', 'black')
                .attr('text-anchor', 'start')
                .style('font', '10px bold');
            growth.append('text')
                .text('<3 Days')
                .attr('x', 250)
                .attr('y', 55)
                .attr('fill', 'black')
                .attr('text-anchor', 'end')
                .style('font', '10px bold');
        });
    } else {
        d3.select('#popover').attr('data-toggle', 'popover')
            .attr('data-placement', 'right')
            .attr('title', d.properties.name)
            .attr('data-content', 'Data unavailable.');
        $(`[title="${d.properties.name}"]`).popover('show');
    }
};

let zoom = function(d) {
    $('[data-toggle="popover"]').popover('dispose');
    let bbox = d3.select('#main').node().getBoundingClientRect();
    $('#popover').css({top: bbox.top+bbox.height/2+window.scrollY, left: bbox.right-bbox.width*0.1-220});

    let x, y, k, c_factor;
    if (center != d.properties.name) {
        center = d.properties.name;
        let centroid = path.centroid(d);
        x = centroid[0];
        y = centroid[1];
        let bounds = path.bounds(d);
        let width_scale = 0.8 * width / (bounds[1][0] - bounds[0][0]);
        let height_scale = 0.8 * height / (bounds[1][1] - bounds[0][1]);
        k = height_only.includes(center) ? height_scale : Math.min(width_scale, height_scale);
        c_factor = 0.35;
        popover(d3.select(this), d);
    } else {
        center = null;
        x = width / 2;
        y = height / 2;
        k = 1;
        c_factor = 0.5;
    }

    d3.select('.countries').selectAll('path')
        .attr('stroke', (d) => {
            return center && center == d.properties.name? '#000001':null;
        });

    d3.select('.countries').transition()
        .duration(1000)
        .attr('transform', `translate(${width * c_factor},${height / 2})scale(${k})translate(${-x},${-y})`);
};

let render = (data) => {
    if (timer != null) timer.stop();
    date = new Date('2020-01-22');
    d3.selectAll('svg *').remove();
    resume_btn.removeAttribute('disabled');
    resume_btn.style.pointerEvents = null;
    slider.value = 0;

    map_data.then(d => {
        let countries = topojson.feature(d, d.objects.countries);
        d3.select('#main').append('g')
            .classed('countries', true)
            .selectAll('path')
                .data(countries.features)
                .join('path')
                .attr('d', path)
                .attr('fill', d => color(get_percent(d, data)))
                .classed('has_data', d => color(get_percent(d, data)) != 'rgb(204, 204, 204)')
                .on('mouseover', highlight)
                .on('mousemove', display_tooltip)
                .on('mouseleave', hide_tooltip)
                .on('click', zoom);

        d3.select('#scale').append('image')
            .attr('x', 50)
            .attr('y', 10)
            .attr('width', 10)
            .attr('height', 320)
            .attr('preserveAspectRatio', 'none')
            .attr('xlink:href', ramp_vertical(color.interpolator()).toDataURL());

        let scale = color.copy();
        scale = Object.assign(scale.domain(scale.domain().map(v => 100 * v))
            .interpolator(d3.interpolateRound(0, 320)), {range() {return [0, 320];}
        });
        let tickAdjust = g => {
            g.selectAll('.tick line').attr('x2', 20).attr('x1', 0);
        };
        d3.select('#scale').append('g')
            .attr('transform', 'translate(40,10)')
            .call(d3.axisLeft(scale)
                .ticks(5)
                .tickSize(10))
            .call(tickAdjust)
            .call(g => g.select('.domain').remove())
            .call(g => g.append('text')
                .text(mode=='Cases'? '% of Population':'% of Cases')
                .attr('x', 0)
                .attr('y', 340)
                .attr('fill', 'black')
                .attr('text-anchor', 'middle')
                .style('font', 'bold'));

        d3.select('#date').append('text')
            .attr('x', '50%')
            .attr('y', '50%')
            .attr('text-anchor', 'middle')
            .text(get_date_formatted())
            .style('font', 'bold 30px sans-serif')
            .classed('date', true);
    });
};

let pause = () => {
    date = new Date('2020-01-22');
    date.setDate(date.getDate() + parseInt(slider.value));
    d3.select('.date').text(get_date_formatted());

    if (timer != null) timer.stop();

    resume_btn.removeAttribute('disabled');
    resume_btn.style.pointerEvents = null;
    pause_btn.setAttribute('disabled', '');
    pause_btn.style.pointerEvents = 'none';
};

let update_map = () => {
    let index = Math.floor((date - new Date('2020-01-22'))/(1000*60*60*24));
    let focus = d3.select('.has_data[stroke="#000001"]');
    if (focus.node() != null) {
        let data = d3.select('#popover').data()[0];
        d3.select('#pop-c').text(data['cases'][index]);
        d3.select('#pop-d').text(data['deaths'][index]);
        d3.select('#pop-r').text(data['recoveries'][index]);
    };

    let has_data = d3.selectAll('.has_data').transition()
        .duration(100);
    switch (mode) {
        case 'Cases':
            has_data.attr('fill', d => color(get_percent(d, data_full)));
            break;
        case 'Deaths':
            data_deaths.then(D => has_data.attr('fill', d => get_percent(d, D)));
            break;
        default:
            data_recovered.then(D => has_data.attr('fill', d => get_percent(d, D)));
    }
};

let advance = () => {
    resume_btn.setAttribute('disabled', '');
    resume_btn.style.pointerEvents = 'none';
    pause_btn.removeAttribute('disabled');
    pause_btn.style.pointerEvents = null;

    let slider_pos = parseInt(slider.value)

    timer = d3.interval((elapsed) => {
        date.setDate(date.getDate() + 1);
        d3.select('.date').text(get_date_formatted());

        let hover = document.querySelectorAll(':hover');
        let country = hover[hover.length - 1];
        if (country !== undefined && country.tagName == 'path') {
            d3.select('#tooltip')
                .attr('data-original-title', format_tooltip(d3.select(country).data()[0]));
            $('[data-toggle="tooltip"]').tooltip('hide');
            $('[data-toggle="tooltip"]').tooltip('show');
        }

        slider.value = parseInt(slider.value) + 1;

        update_map();
    }, 150);
};

let update = () => {
    date = new Date('2020-01-22');
    date.setDate(date.getDate() + parseInt(slider.value));
    d3.select('.date').text(get_date_formatted());

    if (timer != null) timer.stop();

    if (parseInt(slider.value) < range) {
        resume_btn.removeAttribute('disabled');
        resume_btn.style.pointerEvents = null;
    } else {
        resume_btn.setAttribute('disabled', '');
        resume_btn.style.pointerEvents = 'none';
    }

    update_map();
};

let change_data = () => {
    mode = selector.value;
    switch (mode) {
        case 'Cases':
            color.domain([0,0.005])
                .interpolator(d3.interpolateRgbBasis(['#cccccd', 'red', 'firebrick']));
            render(data_full);
            break;
        case 'Deaths':
            data_deaths.then(d => {
                color.domain([0,0.2])
                    .interpolator(d3.interpolateRgbBasis(['#cccccd', 'purple', 'indigo']));
                render(d);
            });
            break;
        default:
            data_recovered.then(d => {
                color.domain([0,0.5])
                    .interpolator(d3.interpolateRgbBasis(['#cccccd', 'lightblue', 'darkblue']));
                render(d);
            });
    }
};

resume_btn.style.pointerEvents = 'none';
$('#selector').selectpicker('render');
d3.select('#map').append('svg')
    .attr('id', 'scale')
    .attr('width', 80)
    .attr('height', 360)
    .style('max-height', '85vh');
d3.select('#map').append('svg')
    .attr('viewBox', [0, 0, width, height])
    .attr('id', 'main')
    .attr('width', width)
    .style('max-width', '80vw')
    .style('max-height', '85vh');
d3.select('#date-container').append('svg')
    .attr('id', 'date');

resume_btn.addEventListener('click', advance);
pause_btn.addEventListener('click', pause)
slider.addEventListener('input', update);
selector.addEventListener('change', change_data);
