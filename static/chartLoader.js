const instantiateChart = (chart_tag, data_obj) => {
    switch (data_obj.chartType) {
        default:
            data = {
                series: [{
                    name: 'series-1',
                    data: data_obj.map(i => ({ x: new Date(i.start_time), y: i.price })),
                }]
            };
            options = {
                axisX: {
                    type: Chartist.FixedScaleAxis,
                    divisor: 5,
                    labelInterpolationFnc: function (value) {
                        return moment(value).format('MMM D');
                    }
                }
            }
            new Chartist.Line('.ct-chart', data, options);
            break
    }
}

document.addEventListener("DOMContentLoaded", () =>
    document.querySelectorAll('.ct-chart').forEach(chart_tag =>
        fetch(chart_tag.getAttribute("url-path"))
            .then(res => res.ok ? res.json() : Promise.reject(res.status))
            .then(data => instantiateChart(chart_tag, data))
            .catch(error => console.error(error))));
