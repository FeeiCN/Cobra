$(document).ready(function () {
    $('#rule_filter').multiselect({
        enableClickableOptGroups: true
    });
});

$('#submit_search').click(function () {
    $.ajax({
        type: 'POST',
        url: '/api/search',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify({sid: getParameterByName('sid'), rule_name: $('#rule_filter').val()}),
        dataType: 'json',
        success: function (result) {
            if (result.code === 1001) {
                alert(result.code);
            }
        }
    })
});