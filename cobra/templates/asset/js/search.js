$(document).ready(function () {
    $('#rule_filter').multiselect({
        enableClickableOptGroups: false
    });
});

function createTable(table, data) {
    // 清空数据
    table.empty();

    // 表头
    var thead = $('<thead></thead>');
    var trs = $('<tr></tr>');
    trs.append($('<th>Target</th>'));
    trs.append($('<th>Branch / Tag</th>'));
    var rules = Object.keys(data[0].search_result).sort();
    for (var i = 0; i < rules.length; i++) {
        trs.append($('<th>' + rule_ids[rules[i]] + '</th>'));
    }
    thead.append(trs);
    table.append(thead);

    // 填充内容
    var tbody = $('<tbody></tbody>');
    for (i = 0; i < data.length; i++) {
        // 每一行
        var row_data = data[i];
        trs = $('<tr></tr>');
        // target
        var s_sid = row_data.target_info.sid;
        var target = row_data.target_info.target;
        var branch = row_data.target_info.branch;
        trs.append($('<td>' + target + '</td>'));
        trs.append($('<td>' + branch + '</td>'));
        // 漏洞数量
        for (var j = 0; j < rules.length; j++) {
            trs.append($('<td>' + row_data.search_result[rules[j]] + '</td>'));
        }
        tbody.append(trs);
    }
    table.append(tbody);
}

$('#submit_search').click(function () {
    $.ajax({
        type: 'POST',
        url: '/api/search',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify({sid: getParameterByName('sid'), rule_id: $('#rule_filter').val()}),
        dataType: 'json',
        success: function (result) {
            if (result.code === 1001) {
                createTable($('#search_table'), result.result);
            } else {
                alert(result.msg);
            }
        }
    })
});