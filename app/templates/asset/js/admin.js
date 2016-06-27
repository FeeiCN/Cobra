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


function showAlert(tag, msg, div) {
    var tt = '<div class="alert alert-' + tag +' alert-dismissible" role="alert">';
    tt += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
    tt += '<span aria-hidden="true">&times;</span></button>';
    tt += '<strong>' + msg + '</strong></div>';
    $(div).html(tt).fadeIn(1000);
}

function make_pagination(cp, t) {
    // make pagination
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
        $("#main-div").load(t + '/' + (cp-1));
    }
    make_pagination(cp-1, t);
}

function next(cp, tp, t) {
    if (cp >= tp) {
        $("#main-div").load(t + '/1');
    } else {
        $("#main-div").load(t + '/' + (cp+1));
    }
    make_pagination(cp+1, t);
}

// delegate search bar
$("#search_rules_bar").delegate("button", "click", function (event) {

    $("#paginate").html("");
    event.preventDefault();

    var language = $("#language").val();
    var vul = $("#vul").val();

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
                var regex = $("#regex").val();
                var description = $("#description").val();
                var regex_confirm = $("#confirm-regex").val();
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
                if (!regex || regex == "") {
                    showAlert('danger', 'regex can not be blank.', '#edit-rule-result');
                    return false;
                }
                if (!regex_confirm || regex_confirm == "") {
                    showAlert('danger', 'confirm regex can not be blank', '#edit-rule-result');
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
                    'regex': regex,
                    'regex_confirm': regex_confirm,
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
        });
        } else if (type === 'view') {
            var regex = $("<div/>").text($("#rule-regex-" + cid).text()).html();
            var confirm_regex = $("<div/>").text($("#rule-confirm-regex-" + cid).text()).html();
            var repair = $("<div/>").text($("#rule-repair-" + cid).text()).html();
            var level = $("<div/>").text($("#rule-level-"+cid).text()).html();
            console.log(level);
            $("#view-title").html("Rule Details.");
            var content = "<b>Regex: </b>" + regex + "<br />";
            content += "<b>Confirm Regex: </b>" + confirm_regex + "<br />";
            content += "<b>Repair: </b>" + repair + "<br />";
            content += "<b>Level: </b>" + level + "<br />";
            $("#view-body").html(content);
        } else if (type === "del") {
            $.post('del_rule', {'rule_id':cid}, function (data) {
            var tt = '<div class="alert alert-' + data.tag +' alert-dismissible" role="alert">';
            tt += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
            tt += '<span aria-hidden="true">&times;</span></button>';
            tt += '<strong>' + data.msg + '</strong></div>';
            $("#operate_result").html(tt).fadeIn(1000);
            $("#show_all_rules").click();
        });
        }

    } else if (target === "vul") {
        if (type === 'view') {
            var repair = $("<div/>").text($("#vul-repair-" + cid).text()).html();
            $("#view-title").html("Vul Details.");
            var content = "<b>Repair: </b>" + repair + "<br />";
            $("#view-body").html(content);
        } else if (type === "del") {
            $.post('del_vul', {'vul_id':cid}, function (result) {
                showAlert(result.tag, result.msg, "#operate_result");
                $("#show_all_vuls").click();
            });
        } else if (type === "edit") {
            $.get('edit_vul/'+ cid, function (data) {
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
        if (type === "edit") {
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
                        'repository' : repository,
                        'author': author,
                        'remark': remark
                    };
                    $.post('edit_project/'+cid, data, function (res) {
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
            $.get('edit_whitelist/'+cid, function (data) {
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

                    $.post("edit_whitelist/"+cid, data, function (result) {
                        showAlert(result.tag, result.msg, '#edit-whitelist-result');
                    });
                });
            });
        }
    } else if (target == "language") {
        if (type == "del") {
            $.post("del_language", {id:cid}, function (data) {
                showAlert(data.tag, data.msg, "#operate_result");
                $("#show_all_languages").click();
            })
        } else if (type == "edit") {
            $.get("edit_language/"+cid, function (data) {
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

                    $.post("edit_language/"+cid, data, function (data) {
                        showAlert(data.tag, data.msg, "#edit-language-result");
                        return false;
                    });

                });
            })
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
    $("#search_rules_bar").load('search_rules_bar');

});

// add new rules
$("#add_new_rules").click(function () {
    $.get('add_new_rule', function (data) {
        $("#main-div").html(data);

        $("#add-new-rule-button").click(function () {
            var vul_type = $("#vul_type").val();
            var lang = $("#language").val();
            var regex = $("#regex").val();
            var regex_confirm = $("#confirm-regex").val();
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
            if (!regex || regex == "") {
                showAlert('danger', 'regex can not be blank.', '#add-new-rule-result');
                return false;
            }
            if (!regex_confirm || regex_confirm == "") {
                showAlert('danger', 'regex confirm can not be blank.', '#add-new-rule-result');
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
                'regex': regex,
                'regex_confirm': regex_confirm,
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

// show all vuls
$("#show_all_vuls").click(function () {

    $.get('vuls/1', function (data) {
        $("#main-div").html(data);
    });

    make_pagination(1, 'vuls');
});

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

// show all projects click
$("#show_all_projects").click(function () {

    $.get('projects/1', function (data) {
        $("#main-div").html(data);
    });

    make_pagination(1, 'projects');
});

// show all white lists click
$("#show_all_whitelists").click(function () {
    $.get('whitelists/1', function (data) {
        $("#main-div").html(data);
    });

    make_pagination(1, 'whitelists');
});

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

$("#show_all_languages").click(function () {
    $("#main-div").load("languages");
    make_pagination(1, 'languages');
});


// dashboard click
$("#show_dashboard").click(function () {
    $("#operate_result").html("");
    $("#search_rules_bar").html("");
    $("#main-div").load("dashboard");
});
