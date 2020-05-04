let selector = document.getElementById('selector');
let trans_btn = document.getElementById('transition');
let slider = document.getElementById('slider');

let map_url = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-10m.json';
let width = 1000;
let height = 500;
let date, timer, center;
let height_only = ['United States of America', 'France', 'Russia', 'Fiji'];

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
    slider.removeAttribute('disabled');
    render();
});

let map_data = d3.json(map_url)
let get_percent = (d) => {
    let data_dated = data_full[get_date()];
    if (data_dated.hasOwnProperty(d.properties.name)) {
        return data_dated[d.properties.name][0];
    } else return undefined;
};
let get_cases = (d) => {
    let data_dated = data_full[get_date()];
    if (data_dated !== undefined && data_dated.hasOwnProperty(d.properties.name)) {
        return data_dated[d.properties.name][1].toLocaleString();
    } else return 0;
};

let color = d3.scaleSequential()
    .domain([0, 0.002])
    .interpolator(d3.interpolateRgbBasis(['#cccccd', 'red', 'black']))
    .unknown('#ccc');

let format_tooltip = (d) => {
    return '<b>' + d.properties.name + `</b><br>${selector.value}: ` + get_cases(d)
};

let display_tooltip = (d) => {
    $('#tooltip').css({top: d3.event.pageY, left: d3.event.pageX});
    d3.select('.tooltip').style('pointer-events', 'none');
    d3.select('#tooltip').attr('data-original-title', format_tooltip(d));
    $('[data-toggle="tooltip"]').tooltip('show');
};

let hide_tooltip = () => {
    $('[data-toggle="tooltip"]').tooltip('hide');
};

let ramp = (color, n = 256) => {
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

let zoom = (d) => {
    let x, y, k;
    if (center != d.properties.name) {
        center = d.properties.name;
        let centroid = path.centroid(d);
        x = centroid[0];
        y = centroid[1];
        let bounds = path.bounds(d);
        let width_scale = 0.8 * width / (bounds[1][0] - bounds[0][0]);
        let height_scale = 0.8 * height / (bounds[1][1] - bounds[0][1]);
        k = height_only.includes(center) ? height_scale : Math.min(width_scale, height_scale);
    } else {
        center = null;
        x = width / 2;
        y = height / 2;
        k = 1;
    }
    d3.select('g').transition()
        .duration(1000)
        .attr('transform', `translate(${width / 2},${height / 2})scale(${k})translate(${-x},${-y})`);
};

let render = () => {
    if (timer != null) timer.stop();
    date = new Date('2020-01-22');
    d3.selectAll('svg *').remove();
    trans_btn.removeAttribute('disabled');
    trans_btn.style.pointerEvents = null;
    slider.value = 0;

    map_data.then(d => {
        let countries = topojson.feature(d, d.objects.countries);
        d3.select('svg').append('g').selectAll('path')
            .data(countries.features)
            .join('path')
            .attr('d', path)
            .attr('fill', d => color(get_percent(d)))
            .classed('has_data', d => color(get_percent(d)) == 'rgb(204, 204, 205)')
            .on('mousemove', display_tooltip)
            .on('mouseleave', hide_tooltip)
            .on('click', zoom);

        d3.select('svg').append('image')
            .attr('x', 100)
            .attr('y', 90)
            .attr('width', 10)
            .attr('height', 320)
            .attr('preserveAspectRatio', 'none')
            .attr('xlink:href', ramp(color.interpolator()).toDataURL());

        let scale = Object.assign(color.copy().domain([0, 0.2]).interpolator(
            d3.interpolateRound(0, 320)), {
            range() {
                return [0, 320];
            }
        });
        let tickAdjust = g => {
            g.selectAll('.tick line').attr('x2', 10).attr('x1', -10);
        };
        d3.select('svg').append('g')
            .attr('transform', 'translate(100,90)')
            .call(d3.axisLeft(scale)
                .ticks(5)
                .tickSize(10))
            .call(tickAdjust)
            .call(g => g.select('.domain').remove())
            .call(g => g.append('text')
                .text('% of Population')
                .attr('x', 0)
                .attr('y', 340)
                .attr('fill', 'black')
                .attr('text-anchor', 'middle')
                .style('font', 'bold'));

        d3.select('svg').append('text')
            .attr('x', '50%')
            .attr('y', height - 8)
            .attr('text-anchor', 'middle')
            .text(get_date_formatted())
            .style('font', 'bold 30px sans-serif')
            .classed('date', true);
    });
};

let advance = () => {
    trans_btn.setAttribute('disabled', '');
    trans_btn.style.pointerEvents = 'none';

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

        d3.selectAll('.has_data').transition()
            .duration(100)
            .attr('fill', d => color(get_percent(d)));

        if (elapsed > 150 * (100 - slider_pos)) timer.stop();
    }, 150);
};

let update = () => {
    date = new Date('2020-01-22');
    date.setDate(date.getDate() + parseInt(slider.value));
    d3.select('.date').text(get_date_formatted());

    if (timer != null) timer.stop();

    if (parseInt(slider.value) < 100) {
        trans_btn.removeAttribute('disabled');
        trans_btn.style.pointerEvents = null;
    } else {
        trans_btn.setAttribute('disabled', '');
        trans_btn.style.pointerEvents = 'none';
    }

    d3.selectAll('.has_data').transition()
            .duration(100)
            .attr('fill', d => color(get_percent(d)));
};

let change_data = () => {
    data_full = d3.json(`/data/${selector.value.toLowerCase()}`).then(d => {
        data_full = d;
        if (selector.value == 'Cases') {
            color.interpolator(d3.interpolateRgbBasis(['#cccccd', 'red', 'black']));
        } else if (selector.value == 'Deaths') {
            color.interpolator(d3.interpolateRgbBasis(['#cccccd', 'black']))
        } else {
            color.interpolator(d3.interpolateRgbBasis(['#cccccd', 'lightblue', 'blue']))
        }
        render();
    });
};

trans_btn.style.pointerEvents = 'none';
$('#selector').selectpicker('render');
d3.select('#map').append('svg').attr('viewBox', [0, 0, width, height])
    .style('max-height', '85vh');

trans_btn.addEventListener('click', advance);
slider.addEventListener('input', update);
selector.addEventListener('change', change_data);
