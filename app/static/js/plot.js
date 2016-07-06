$(document).ready(function() {
	$(chart_id).highcharts({
        data: {
            table: 'hidden_table'
        },
        chart: {
        	renderTo: 'chart_id',
            type: 'column'
        },
        title: {
            text: ''
        },
        yAxis: yAxis,
        tooltip: {
            formatter: function () {
                return '<b>' + this.series.name + '</b><br/>' +
                    this.point.y + ' ' + this.point.name.toLowerCase();
            }
        }
    });
});
       