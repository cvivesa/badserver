const instantiateChart = series => {
    data = {
        series: series.map(s => ({
            data: s.map(i => ({ x: new Date(i[0]), y: i[1] }))
        }))
    };
    options = {
        axisX: {
            type: Chartist.FixedScaleAxis,
            divisor: 5,
            labelInterpolationFnc: value => moment(value).format('MMM D'),
            // showGrid: false,
        },
        axisY: {
            type: Chartist.AutoScaleAxis,
            scaleMinSpace: 50,
            // showGrid: false,
        },
    }
    let chart = new Chartist.Line('.ct-chart', data, options);

    chart.on('draw', data => {
        if (data.type === 'grid' && data.index !== 0) {
            data.element.remove();
        }
    });
}
const hoverHandler = e => {
    let el = e.target.firstElementChild
    if (!el) return;
    let num = el.textContent.slice(-1);

    fetch(document.querySelector('.ct-chart').getAttribute("url-path") + num)
        .then(res => res.ok ? res.json() : Promise.reject(res.status))
        .then(data => instantiateChart(data))
        .catch(error => console.error(error));

    // could navigate from chart to title and update

    document.querySelectorAll('.map > path')
        .forEach(el => el.style.display = 'none');
    document.querySelector('.map > path.p' + num).style.display = 'inline'

    document.querySelector('#chart-title').textContent = 'Surge ' + num;
}

document.addEventListener("DOMContentLoaded", () => {
    fetch(document.querySelector('.ct-chart').getAttribute("url-path"))
        .then(res => res.ok ? res.json() : Promise.reject(res.status))
        .then(data => instantiateChart(data))
        .catch(error => console.error(error));

    document.querySelectorAll('tbody tr')
        .forEach(el => el.addEventListener('mouseover', hoverHandler));
});
