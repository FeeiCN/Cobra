/**
 * Created by lightless on 16/5/30.
 */


$(document).ready(function () {
    $("#show_dashboard").click();
    $("#main-div").fadeIn(1000);
});

$("#left-div button").click(function () {
    $("button").removeClass('btn-success');
    $(this).addClass('btn-success');
});

$("[id^=add_new_]").click(function () {
    $("#paginate").html("");
    $("#search_rules_bar").html("");
});
$("[id^=show_all_]").click(function () {
    $("#search_rules_bar").html("")
});

var g_rule_back_page = 1;
var g_rule_back_lang = null;
var g_rule_back_vul = null;
var g_rule_back_method = null;

function showAlert(tag, msg, div) {
    var tt = '<div class="alert alert-' + tag + ' alert-dismissible" role="alert">';
    tt += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
    tt += '<span aria-hidden="true">&times;</span></button>';
    tt += '<strong>' + msg + '</strong></div>';
    $(div).html(tt).fadeIn(1000);
}

function make_pagination(cp, t) {
    // make pagination
    g_rule_back_page = cp;
    g_rule_back_method = "page";
    // get all rules count first
    var all_count = 0;
    var promise = $.ajax('all_' + t + '_count');
    promise.always(function (data) {
        all_count = data;
        var per_page_count = 10;
        var total_pages = Math.ceil(all_count / per_page_count);
        var current_page = cp;

        var pp = "<ul class='pagination'>";
        pp += "<li><a href='#' id='prev' role='button' class='btn' style='outline: none;' " +
            "onclick=prev(" + current_page + ",\"" + t + "\")>Prev</a></li>";
        pp += "<li><a href='#' class='disabled'>" + current_page + " / " + total_pages + "</a></li>";
        pp += "<li><a href='#' id='next' role='button' class='btn' style='outline: none;' " +
            "onclick=next(" + current_page + "," + total_pages + ",\"" + t + "\")>Next</a></li>";
        pp += "</ul>";

        $("#paginate").html(pp);

        if (current_page == 1) {
            $("#prev").addClass('disabled')
        }
        if (current_page == total_pages) {
            $("#next").addClass('disabled')
        }

    });
}

function prev(cp, t) {
    if (cp <= 1) {
        $("#main-div").load(t + '/1');
    } else {
        $("#main-div").load(t + '/' + (cp - 1));
    }
    make_pagination(cp - 1, t);
}

function next(cp, tp, t) {
    if (cp >= tp) {
        $("#main-div").load(t + '/1');
    } else {
        $("#main-div").load(t + '/' + (cp + 1));
    }
    make_pagination(cp + 1, t);
}

// delegate search bar
$("#search_rules_bar").delegate("button#search_rules_button", "click", function (event) {

    $("#paginate").html("");
    event.preventDefault();

    var language = $("#search_language").val();
    var vul = $("#vul").val();
    g_rule_back_lang = language;
    g_rule_back_vul = vul;
    g_rule_back_method = "search";

    data = {
        'language': language,
        'vul': vul
    };

    $.post('search_rules', data, function (data) {
        $("#main-div").html(data);
    });

});

// delegate main-div
$("#main-div").delegate("span", "click", function () {
    var cur_id = $(this).attr('id');
    var type = cur_id.split('-')[0];
    var target = cur_id.split('-')[1];
    var cid = cur_id.split('-')[2];

    if (type === "edit") {
        $("#paginate").html("");
        $("#search_rules_bar").html("");
    }

    if (target === "rule") {
        if (type === 'edit') {
            $.get('edit_rule/' + cid, function (result) {
                $('#main-div').html(result);

                $("#edit-rule-button").click(function () {
                    var vul_type = $("#vul_type").val();
                    var lang = $("#language").val();
                    var regex_location = $("#regex-location").val();
                    var description = $("#description").val();
                    var regex_repair = $("#regex-repair").val();
                    var block_reapir = $("#repair-block:checked").val();
                    var repair = $("#repair").val();
                    var status = $("#status:checked").val();
                    var level = $("#level:checked").val();

                    // check data
                    if (!vul_type || vul_type == "") {
                        showAlert('danger', 'vul type error.', '#edit-rule-result');
                        return false;
                    }
                    if (!lang || lang == "") {
                        showAlert('danger', 'language error.', '#edit-rule-result');
                        return false;
                    }
                    if (!description || description == "") {
                        showAlert('danger', 'description can not be blank.', '#edit-rule-result');
                        return false;
                    }
                    if (!regex_location || regex_location == "") {
                        showAlert("danger", "regex location cannot be blank.", "#edit-rule-result");
                        return false;
                    }
                    if (!regex_repair || regex_repair == "") {
                        showAlert("danger", "regex repair cannot be blank.", "#edit-rule-result");
                        return false;
                    }
                    if (!block_reapir || block_reapir == "") {
                        showAlert("danger", "block repair cannot be blank.", "#edit-rule-result");
                        return false;
                    }
                    if (!repair || repair == "") {
                        showAlert('danger', 'repair can not be blank.', '#edit-rule-result');
                        return false;
                    }
                    if (!status || status == "") {
                        showAlert('danger', 'status error.', '#edit-rule-result');
                        return false;
                    }
                    if (!level || level == "") {
                        showAlert('danger', 'level can not be blank.', '#edit-rule-result');
                        return false;
                    }

                    // post data
                    var data = {
                        'vul_type': vul_type,
                        'language': lang,
                        'regex_location': regex_location,
                        'regex_repair': regex_repair,
                        'block_repair': block_reapir,
                        'description': description,
                        'rule_id': cid,
                        'repair': repair,
                        'status': status,
                        'level': level
                    };
                    $.post('edit_rule/' + cid, data, function (res) {
                        showAlert(res.tag, res.msg, "#edit-rule-result");
                    });
                });

                $("#back-rule-button").click(function () {
                    // back to rule list.
                    if (g_rule_back_method == "search") {
                        data = {
                            'language': g_rule_back_lang,
                            'vul': g_rule_back_vul
                        };
                        $.post('search_rules', data, function (data) {
                            $("#main-div").html(data);
                        });
                        $.get("search_rules_bar", function (raw_data) {
                            $("#search_rules_bar").html(raw_data);
                            $("#vul").val(g_rule_back_vul);
                            $("#language").val(g_rule_back_lang);
                        });

                    } else if (g_rule_back_method == "page") {
                        var back_page = g_rule_back_page;
                        $.get('rules/' + back_page, function (data) {
                            $("#main-div").html(data);
                        });

                        make_pagination(back_page, 'rules');

                        // show search bar
                        $("#search_rules_bar").load('search_rules_bar');
                    }


                });
            });
        } else if (type === 'view') {
            var regex = $("<div/>").text($("#rule-regex-" + cid).text()).html();
            var confirm_regex = $("<div/>").text($("#rule-confirm-regex-" + cid).text()).html();
            var repair = $("<div/>").text($("#rule-repair-" + cid).text()).html();
            var level = $("<div/>").text($("#rule-level-" + cid).text()).html();
            console.log(level);
            $("#view-title").html("rule details.");
            var content = "<b>regex: </b>" + regex + "<br />";
            content += "<b>confirm regex: </b>" + confirm_regex + "<br />";
            content += "<b>repair: </b>" + repair + "<br />";
            content += "<b>level: </b>" + level + "<br />";
            $("#view-body").html(content);
        } else if (type === "del") {
            $.post('del_rule', {'rule_id': cid}, function (data) {
                var tt = '<div class="alert alert-' + data.tag + ' alert-dismissible" role="alert">';
                tt += '<button type="button" class="close" data-dismiss="alert" aria-label="close">';
                tt += '<span aria-hidden="true">&times;</span></button>';
                tt += '<strong>' + data.msg + '</strong></div>';
                $("#operate_result").html(tt).fadein(1000);
                $("#show_all_rules").click();
            });
        }

    } else if (target === "vul") {
        if (type === 'view') {
            var repair = $("<div/>").text($("#vul-repair-" + cid).text()).html();
            $("#view-title").html("vul details.");
            var content = "<b>repair: </b>" + repair + "<br />";
            $("#view-body").html(content);
        } else if (type === "del") {
            $.post('del_vul', {'vul_id': cid}, function (result) {
                showAlert(result.tag, result.msg, "#operate_result");
                $("#show_all_vuls").click();
            });
        } else if (type === "edit") {
            $.get('edit_vul/' + cid, function (data) {
                $("#main-div").html(data);
                $("#edit-vul-button").click(function () {
                    var name = $("#name").val();
                    var description = $("#description").val();
                    var repair = $("#repair").val();

                    if (!name || name == "") {
                        showAlert('danger', 'name can not be blank.', '#edit-vul-result');
                        return false;
                    }
                    if (!description || description == "") {
                        showAlert('danger', 'description can not be blank.', '#edit-vul-result');
                        return false;
                    }
                    if (!repair || repair == "") {
                        showAlert('danger', 'repair can not be blank.', '#edit-vul-result');
                        return false;
                    }

                    data = {
                        'vul_id': cid,
                        'name': name,
                        'description': description,
                        'repair': repair
                    };
                    $.post('edit_vul/' + cid, data, function (res) {
                        showAlert(res.tag, res.msg, '#edit-vul-result');
                    });
                });

            });
        }

    } else if (target === "project") {
        if (type === "run") {
            var project_id = cid;
            //$(".containter").plainoverlay('show');
            var data = {'project_id': project_id, 'key': '0dcbe720a3c93b2ab0070b0d5294a97a'}
            $.ajax({
                'url': '/api/add',
                'type': 'post',
                'data': JSON.stringify(data),
                'datatype': 'json',
                'async': true,
                'contentType': 'application/json;charset=utf-8',
                'success': function (result) {
                    if (result.code == 1001) {
                        var scan_id = result.result['scan_id'];
                        var data = {'scan_id': scan_id, 'key': '0dcbe720a3c93b2ab0070b0d5294a97a'};

                        function get_status() {
                            $.ajax({
                                'url': '/api/status',
                                'type': 'POST',
                                'data': JSON.stringify(data),
                                'dataType': 'json',
                                'async': false,
                                'contentType': 'application/json;charset=utf-8',
                                'success': function (result) {
                                    if (result.result['status'] == 'done') {
                                        alert('Scanning project ' + project_id + ' done.');
                                        window.open(result.result['report'], '_blank');
                                    }
                                    else {
                                        setTimeout(get_status, 300);
                                    }
                                }
                            });
                        }

                        get_status();

                    }
                    else {
                        alert(result.result);
                    }
                }
            });
        }
        if (type === "add") {
            $.get("add_project/", function (data) {
                $("#main-div").html(data);
                $("add-project-button").click(function () {
                    var name = $("#name").val();
                    var repository = $("#repository").val();
                    var author = $("#author").val();
                    var remark = $("#remark").val();

                    if (!name || name == "") {
                        showAlert('danger', 'name can not be empty!', 'add-project-result');
                        return false;
                    }
                    if (!repository || repository == "") {
                        showAlert('danger', 'repository can not be empty!', '#add-project-result');
                        return false;
                    }
                    if (!remark || remark == "") {
                        showAlert('danger', 'remark can not be empty!', '#add-project-result');
                        return false;
                    }
                    if (!author || author == "") {
                        showAlert('danger', 'author cannot be empty!', '#add-project-result');
                        return false;
                    }

                    data = {
                        'name': name,
                        'repository': repository,
                        'author': author,
                        'remark': remark
                    };
                    $.post('add_project/', data, function (res) {
                        showAlert(res.tag, res.msg, '#add-project-result');
                    });
                });
            });
        }
        else if (type === "edit") {
            $.get("edit_project/" + cid, function (data) {
                $("#main-div").html(data);

                $("#edit-project-button").click(function () {
                    var name = $("#name").val();
                    var repository = $("#repository").val();
                    var author = $("#author").val();
                    var remark = $("#remark").val();

                    if (!name || name == "") {
                        showAlert('danger', 'name can not be empty!', 'edit-project-result');
                        return false;
                    }
                    if (!repository || repository == "") {
                        showAlert('danger', 'repository can not be empty!', '#edit-project-result');
                        return false;
                    }
                    if (!remark || remark == "") {
                        showAlert('danger', 'remark can not be empty!', '#edit-project-result');
                        return false;
                    }
                    if (!author || author == "") {
                        showAlert('danger', 'author cannot be empty!', '#edit-project-result');
                        return false;
                    }

                    data = {
                        'project_id': cid,
                        'name': name,
                        'repository': repository,
                        'author': author,
                        'remark': remark
                    };
                    $.post('edit_project/' + cid, data, function (res) {
                        showAlert(res.tag, res.msg, '#edit-project-result');
                    });
                });
            });
        } else if (type === "del") {
            $.post("del_project", {"id": cid}, function (result) {
                showAlert(result.tag, result.msg, "#operate_result");
                $("#show_all_projects").click();
            });
        }

    } else if (target === "whitelist") {
        if (type === "del") {
            $.post('del_whitelist', {'whitelist_id': cid}, function (data) {
                showAlert(data.tag, data.msg, "#operate_result");
                $("#show_all_whitelists").click();
            });
        } else if (type === "edit") {
            $.get('edit_whitelist/' + cid, function (data) {
                $("#main-div").html(data);

                $("#edit-whitelist-button").click(function () {
                    var project = $("#project").val();
                    var rule = $("#rule").val();
                    var path = $("#path").val();
                    var reason = $("#reason").val();
                    var status = $("#status:checked").val();

                    data = {
                        'whitelist_id': cid,
                        'project': project,
                        'rule': rule,
                        'path': path,
                        'reason': reason,
                        'status': status
                    };

                    $.post("edit_whitelist/" + cid, data, function (result) {
                        showAlert(result.tag, result.msg, '#edit-whitelist-result');
                    });
                });
            });
        }
    } else if (target == "language") {
        if (type == "del") {
            $.post("del_language", {id: cid}, function (data) {
                showAlert(data.tag, data.msg, "#operate_result");
                $("#show_all_languages").click();
            })
        } else if (type == "edit") {
            $.get("edit_language/" + cid, function (data) {
                $("#main-div").html(data);
                $("#edit-language-button").click(function () {
                    var language = $("#language").val();
                    var extensions = $("#extensions").val();

                    if (!language || language == "") {
                        showAlert("danger", "language name can not be blank.", "#edit-language-result");
                        return false;
                    }
                    if (!extensions || extensions == "") {
                        showAlert("danger", "extensions can not be blank.", "#edit-language-result");
                        return false;
                    }

                    data = {
                        'language': language,
                        'extensions': extensions
                    };

                    $.post("edit_language/" + cid, data, function (data) {
                        showAlert(data.tag, data.msg, "#edit-language-result");
                        return false;
                    });

                });
            })
        }
    } else if (target === "task") {
        if (type === "edit") {
            $.get('edit_task/' + cid, function (data) {
                $("#main-div").html(data);

                $("#edit-task-button").click(function () {
                    var branch = $("#branch").val();
                    var scan_way = $("#scanway:checked").val();
                    var old_version = $("#oldversion").val();
                    var new_version = $("#newversion").val();
                    var target = $("#target").val();

                    data = {
                        'branch': branch,
                        'scan_way': scan_way,
                        'old_version': old_version,
                        'new_version': new_version,
                        'target': target
                    };

                    $.post("edit_task/" + cid, data, function (result) {
                        showAlert(result.tag, result.msg, '#edit-task-result');
                    });
                });
            });
        } else if (type === "del") {
            $.post("del_task", {id: cid}, function (data) {
                showAlert(data.tag, data.msg, "#operate_result");
                $("#show_all_tasks").click();
            });
        } else if (type === "view") {
            var old_version = $("<div/>").text($("#task-oldversion-" + cid).text()).html();
            var new_version = $("<div/>").text($("#task-newversion-" + cid).text()).html();
            var time_start = $("<div/>").text($("#task-timestart-" + cid).text()).html();
            var time_end = $("<div/>").text($("#task-timeend-" + cid).text()).html();
            var time_consume = $("<div/>").text($("#task-timeconsume-" + cid).text()).html();
            var status = $("<div/>").text($("#task-status-" + cid).text()).html();
            var code_number = $("<div/>").text($("#task-codenumber-" + cid).text()).html();
            $("#view-title").html("Task Details.");
            var content = "<b>Old Version: </b>" + old_version + "<br />";
            content += "<b>New Version: </b>" + new_version + "<br />";
            content += "<b>Time Start: </b>" + time_start + "<br />";
            content += "<b>Time End: </b>" + time_end + "<br />";
            content += "<b>Time Consume: </b>" + time_consume + "<br />";
            content += "<b>Status: </b>" + status + "<br />";
            content += "<b>Code Number: </b>" + code_number + "<br />";

            $("#view-body").html(content);
        }
    }
});

// show all rules
$("#show_all_rules").click(function () {

    $.get('rules/1', function (data) {
        $("#main-div").html(data);
    });

    make_pagination(1, 'rules');

    // show search bar
    $("#search_rules_bar").load('search_rules_bar', function () {



        // add new rules
        $("#add_new_rules").click(function () {
            $.get('add_new_rule', function (data) {
                $("#main-div").html(data);

                $("#add-new-rule-button").click(function () {
                    var vul_type = $("#vul_type").val();
                    var lang = $("#add-rule-language").val();
                    var regex_location = $("#regex-location").val();
                    var regex_repair = $("#regex-repair").val();
                    var repair_block = $("#repair-block:checked").val();
                    var description = $("#description").val();
                    var repair = $("#repair").val();
                    var level = $("#level:checked").val();

                    // check data
                    if (!vul_type || vul_type == "") {
                        showAlert('danger', 'vul type error.', '#add-new-rule-result');
                        return false;
                    }
                    if (!lang || lang == "") {
                        showAlert('danger', 'language error.', '#add-new-rule-result');
                        return false;
                    }
                    if (!description || description == "") {
                        showAlert('danger', 'description can not be blank.', '#add-new-rule-result');
                        return false;
                    }
                    if (!regex_location || regex_location == "") {
                        showAlert('danger', 'location regex can not be blank.', '#add-new-rule-result');
                        return false;
                    }
                    if (!regex_repair || regex_repair == "") {
                        showAlert('danger', 'repair regex confirm can not be blank.', '#add-new-rule-result');
                        return false;
                    }
                    if (!repair_block || repair_block == "") {
                        showAlert('danger', 'repair block confirm can not be blank.', '#add-new-rule-result');
                        return false;
                    }
                    if (!repair || repair == "") {
                        showAlert('danger', 'repair can not be blank.', '#add-new-rule-result');
                        return false;
                    }
                    if (!level || level == "") {
                        showAlert('danger', 'level can not be blank.', "#add-new-rule-result");
                        return false;
                    }

                    // post data
                    var data = {
                        'vul_type': vul_type,
                        'language': lang,
                        'regex_location': regex_location,
                        'regex_repair': regex_repair,
                        'repair_block': repair_block,
                        'description': description,
                        'repair': repair,
                        'level': level
                    };
                    $.post('add_new_rule', data, function (res) {
                        showAlert(res.tag, res.msg, '#add-new-rule-result');
                    });
                });
            });
        });
    });

});


// show all vuls
$("#show_all_vuls").click(function () {

    $.get('vuls/1', function (data) {
        $("#main-div").html(data);

// Add new vuls.
        $("#add_new_vuls").click(function () {
            $.get('add_new_vul', function (data) {
                $("#main-div").html(data);

                $("#name").focus(function () {
                    $("#add-new-vul-result").fadeOut(1000);
                });
                $("#description").focus(function () {
                    $("#add-new-vul-result").fadeOut(1000);
                });

                $("#add-new-vul-button").click(function () {
                    var name = $("#name").val();
                    var description = $("#description").val();
                    var repair = $("#repair").val();

                    if (name == "" || !name) {
                        showAlert('danger', 'name can not be blank.', '#add-new-vul-result');
                        return false;
                    }
                    if (description == "" || !description) {
                        showAlert('danger', 'description can not be blank.', '#add-new-vul-result');
                        return false;
                    }
                    if (repair == "" || !description) {
                        showAlert('danger', 'description can not be blank.', '#add-new-vul-result');
                        return false;
                    }
                    var data = {
                        'name': name,
                        'description': description,
                        'repair': repair
                    };
                    $.post('add_new_vul', data, function (res) {
                        showAlert(res.tag, res.msg, "#add-new-vul-result");
                    });
                });
            });
        });
    });

    make_pagination(1, 'vuls');
});


// show all projects click
$("#show_all_projects").click(function () {

    $.get('projects/1', function (data) {
        $("#main-div").html(data);
        $("#add_new_project").click(function () {
            $.get('add_new_project', function (data) {
                $("#main-div").html(data);

                $("#add-project-button").click(function () {
                    var name = $("#name").val();
                    var repository = $("#repository").val();
                    var author = $("#author").val();
                    var remark = $("#remark").val();

                    if (!name || name == "") {
                        showAlert('danger', 'name can not be empty!', 'add-project-result');
                        return false;
                    }
                    if (!repository || repository == "") {
                        showAlert('danger', 'repository can not be empty!', '#add-project-result');
                        return false;
                    }
                    if (!remark || remark == "") {
                        showAlert('danger', 'remark can not be empty!', '#add-project-result');
                        return false;
                    }
                    if (!author || author == "") {
                        showAlert('danger', 'author cannot be empty!', '#add-project-result');
                        return false;
                    }

                    data = {
                        'name': name,
                        'repository': repository,
                        'author': author,
                        'remark': remark
                    };
                    $.post('add_new_project/', data, function (res) {
                        showAlert(res.tag, res.msg, '#add-project-result');
                    });

                });

            });
        });
    });

    make_pagination(1, 'projects');
});

// show all white lists click
$("#show_all_whitelists").click(function () {
    $.get('whitelists/1', function (data) {
        $("#main-div").html(data);
        // add new white list click
        $("#add_new_whitelist").click(function () {
            $.get('add_whitelist', function (data) {
                $("#main-div").html(data);

                $("#add-new-whitelist-button").click(function () {
                    var project_id = $("#project").val();
                    var rule_id = $("#rule").val();
                    var path = $("#path").val();
                    var reason = $("#reason").val();

                    if (!project_id || project_id == "") {
                        showAlert('danger', 'project error.', "#add-new-whitelist-result");
                        return false;
                    }

                    if (!rule_id || rule_id == "") {
                        showAlert('danger', 'rule error.', "#add-new-whitelist-result");
                        return false;
                    }

                    if (!path || path == "") {
                        showAlert('danger', 'file cannot be empty.', "#add-new-whitelist-result");
                        return false;
                    }

                    if (!reason || reason == "") {
                        showAlert('danger', 'reason can not be empty', "#add-new-whitelist-result");
                        return false;
                    }

                    data = {
                        'project_id': project_id,
                        'rule_id': rule_id,
                        'path': path,
                        'reason': reason
                    };

                    $.post('add_whitelist', data, function (result) {
                        showAlert(result.tag, result.msg, "#add-new-whitelist-result");
                    });
                });

            });
        });
    });

    make_pagination(1, 'whitelists');
});

$("#show_all_languages").click(function () {
    $("#main-div").load("languages", function () {
        // add new languages
        $("#add_new_language").click(function () {
            $.get("add_new_language", function (data) {
                $("#main-div").html(data);
                $("#add-new-language-button").click(function () {
                    var language = $("#language").val();
                    var extensions = $("#extensions").val();

                    if (!language || language == "") {
                        showAlert("danger", "language name can not be blank.", "#add-new-language-result");
                        return false;
                    }
                    if (!extensions || extensions == "") {
                        showAlert("danger", "extensions can not be blank.", "#add-new-language-result");
                    }

                    data = {
                        "language": language,
                        "extensions": extensions
                    };

                    $.post("add_new_language", data, function (res) {
                        showAlert(res.tag, res.msg, "#add-new-language-result");
                    });
                });
            });
        });
    });
    make_pagination(1, 'languages');
});

// show all tasks click
$("#show_all_tasks").click(function () {
    $("#main-div").load("tasks/1");
    make_pagination(1, "tasks");
});


// add new task click


// dashboard click
$("#show_dashboard").click(function () {
    $("#operate_result").html("");
    $("#search_rules_bar").html("");

    $.get("dashboard", function (data) {
        $("#main-div").html(data);
        $('#start-time').datetimepicker();
        $("#end-time").datetimepicker();
        $("#g-start-time").datetimepicker();
        $("#g-end-time").datetimepicker();

        $("#show-info").click(function () {
            var start_time = $("#start-time").val();
            var end_time = $("#end-time").val();

            var start_time_stamp = new Date(start_time);
            start_time_stamp = start_time_stamp.getTime();

            var end_time_stamp = new Date(end_time);
            end_time_stamp = end_time_stamp.getTime();

            var data = {
                'start_time': start_time,
                'start_time_stamp': start_time_stamp,
                'end_time': end_time,
                'end_time_stamp': end_time_stamp
            };

            $.post("get_scan_information", data, function (res) {

                if (res.code == 1002) {
                    showAlert(res.tag, res.msg, "#information");
                    $("#information").fadeIn(1000);
                } else if (res.code == 1001) {
                    var content = '<br/><table class="table"><tbody>';
                    content += '<tr><td><b>Overview</b></td><td><b>Count</b></td></tr>';
                    content += '<tr><td>Scan Times: </td><td>' + res.task_count + '</td></tr>';
                    content += '<tr><td>Vulnerabilities: </td><td>' + res.vulns_count + '</td></tr>';
                    content += '<tr><td>Scanned Projects Count: </td><td>' + res.projects_count + '</td></tr>';
                    content += '<tr><td>Files Count: </td><td>' + res.files_count + '</td></tr>';
                    content += '<tr><td>Code Number: </td><td>' + res.code_number + '</td></tr>';
                    content += '</tbody></table>';
                    $("#information").html(content);
                    $("#information").fadeIn(1000);
                }
            });

        });

        $("#hide-info").click(function () {
            $("#information").fadeOut(1000);
        });

        // graph colors
        var colors = [
            "#FF6384", "#36A2EB", "#FFCE56", "#2F4F4F", "#32CD32",
            "#FFFF00", "#DAA520", "#FF8C00", "#FF4500", "#B22222",
            "#000000", "#7FFFD4", "#1E90FF", "#C71585", "#0000CD",
            "#E6E6FA", "#FF1493", "#DC143C", "#4682B4", "#00BFFF",
            "#5F9EA0", "#48D1CC", "#00FA9A", "#556B2F", "#FFD700"
        ];

        // draw chart functions
        var chart_vuls = null;
        var chart_languages = null;
        var chart_lines = null;

        function draw_vuls_chart(ctx, data, type) {
            if (chart_vuls != null) {
                chart_vuls.destroy();
            }

            chart_vuls = new Chart(ctx, {
                type: type,
                data: data
            });
        }

        function draw_languages_chart(ctx, data, type) {
            if (chart_languages != null) {
                chart_languages.destroy();
            }

            chart_languages = new Chart(ctx, {
                type: type,
                data: data
            });
        }

        function draw_lines_chart(ctx, data, type) {
            if (chart_lines != null) {
                chart_lines.destroy()
            }

            chart_lines = new Chart(ctx, {
                type: type,
                data: data,
            })
        }

        // draw all data
        $("#show-all-data").click(function () {
            var data = {
                "show_all": 1
            };

            // vulns graph
            $.post("graph_vulns", data, function (raw_data) {
                var labels = [];
                var data = [];
                for (var i = 0; i < raw_data.data.length; i++) {
                    labels.push(raw_data.data[i]["vuls"]);
                    data.push(raw_data.data[i]["counts"]);
                }
                var g_data = {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        hoverBackgroundColor: colors,
                    }]
                };
                var ctx = $("#g-vulns");
                draw_vuls_chart(ctx, g_data, "pie");
            });

            // languages vulns graph
            $.post("graph_languages", data, function (raw_data) {
                var labels = [];
                var data = [];
                for (i in raw_data.data) {
                    labels.push(i);
                    data.push(raw_data.data[i]);
                }
                var g_data = {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        hoverBackgroundColor: colors,
                    }]
                };
                var ctx = $("#g-languages");
                draw_languages_chart(ctx, g_data, "pie");
            });

            // lines graph
            $.post("graph_lines", data, function (raw_data) {
                var g_data = {
                    labels: raw_data.labels,
                    datasets: [
                        {
                            label: "vulnerabilities everyday",
                            fill: false,
                            pointRadius: 5,
                            lineTension: 0,
                            backgroundColor: colors[0],
                            pointBackgroundColor: colors[0],
                            borderColor: colors[0],
                            data: raw_data.vuls
                        },
                        {
                            label: "scan times everyday",
                            fill: false,
                            pointRadius: 5,
                            lineTension: 0,
                            backgroundColor: colors[1],
                            pointBackgroundColor: colors[1],
                            borderColor: colors[1],
                            data: raw_data.scans
                        }
                    ]
                };
                var ctx = $("#g-lines");
                draw_lines_chart(ctx, g_data, "line")
            });

        });

        // draw part of data
        $("#show-data").click(function () {
            var start_time = $("#g-start-time").val();
            var end_time = $("#g-end-time").val();
            var start_time_stamp = new Date(start_time);
            start_time_stamp = start_time_stamp.getTime();
            var end_time_stamp = new Date(end_time);
            end_time_stamp = end_time_stamp.getTime();

            data = {
                "start_time_stamp": start_time_stamp,
                "end_time_stamp": end_time_stamp
            };

            $.post("graph_vulns", data, function (raw_data) {
                var labels = [];
                var data = [];
                for (var i = 0; i < raw_data.data.length; i++) {
                    labels.push(raw_data.data[i]["vuls"]);
                    data.push(raw_data.data[i]["counts"]);
                }
                var g_data = {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        hoverBackgroundColor: colors,
                    }]
                };
                var ctx = $("#g-vulns");
                draw_vuls_chart(ctx, g_data, "pie");
            });

            $.post("graph_languages", data, function (raw_data) {
                var labels = [];
                var data = [];
                for (i in raw_data.data) {
                    labels.push(i);
                    data.push(raw_data.data[i]);
                }
                var g_data = {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        hoverBackgroundColor: colors,
                    }]
                };
                var ctx = $("#g-languages");
                draw_languages_chart(ctx, g_data, "pie");
            });

            $.post("graph_lines", data, function (raw_data) {
                var g_data = {
                    labels: raw_data.labels,
                    datasets: [
                        {
                            label: "vulnerabilities everyday",
                            fill: false,
                            pointRadius: 5,
                            lineTension: 0,
                            backgroundColor: colors[0],
                            pointBackgroundColor: colors[0],
                            borderColor: colors[0],
                            data: raw_data.vuls
                        },
                        {
                            label: "scan times everyday",
                            fill: false,
                            pointRadius: 5,
                            lineTension: 0,
                            backgroundColor: colors[1],
                            pointBackgroundColor: colors[1],
                            borderColor: colors[1],
                            data: raw_data.scans
                        }
                    ]
                };
                var ctx = $("#g-lines");
                draw_lines_chart(ctx, g_data, "line");
            });

        });
        $("#show-all-data").click();


    });


});
