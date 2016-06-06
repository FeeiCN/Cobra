/**
 * Created by lightless on 16/5/30.
 */


$("#main-div").fadeIn(1000);

$("[id^=add_new_]").click(function () {
    $("#paginate").html("");
});


function showAlert(tag, msg, div) {
    var tt = '<div class="alert alert-' + tag +' alert-dismissible" role="alert">';
    tt += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
    tt += '<span aria-hidden="true">&times;</span></button>';
    tt += '<strong>' + msg + '</strong></div>';
    $(div).html(tt).fadeIn(1000);
}

function make_rules_pagination(cp) {
    // make pagination
    // get all rules count first
    var rules_count = 0;
    var promise = $.ajax('all_rules_count');
    promise.always(function (data) {
        rules_count = data;
        var per_page_count = 10;
        var total_pages = Math.ceil(rules_count / per_page_count);
        var current_page = cp;

        var pp = "<ul class='pagination'>";
        pp += "<li><a href='#' id='prev' role='button' class='btn' style='outline: none;' " +
            "onclick='prevRules(" + current_page + ")'>Prev</a></li>";
        pp += "<li><a href='#' class='disabled'>" + current_page + " / " + total_pages + "</a></li>";
        pp += "<li><a href='#' id='next' role='button' class='btn' style='outline: none;' " +
            "onclick='nextRules(" + current_page + "," + total_pages + ")'>Next</a></li>";
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

function prevRules(cp) {
    if (cp <= 1) {
        $("#main-div").load('rules/1');
    } else {
        $("#main-div").load('rules/' + (cp-1));
    }
    make_rules_pagination(cp-1);
}

function nextRules(cp, tp) {
    if (cp >= tp) {
        $("#main-div").load('rules/1');
    } else {
        $("#main-div").load('rules/' + (cp+1));
    }
    make_rules_pagination(cp+1);
}


// delegate here
$("#main-div").delegate("span", "click", function () {
    var cur_id = $(this).attr('id');
    var type = cur_id.split('-')[0];
    var target = cur_id.split('-')[1];
    var cid = cur_id.split('-')[2];
    console.log("[delegate]"+$(this).attr('id'));

    if (type === "edit") {
        $("#paginate").html("");
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

                // post data
                var data = {
                    'vul_type': vul_type,
                    'language': lang,
                    'regex': regex,
                    'regex_confirm': regex_confirm,
                    'description': description,
                    'rule_id': cid,
                    'repair': repair,
                    'status': status
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
            $("#view-title").html("Rule Details.");
            var content = "<b>Regex: </b>" + regex + "<br />";
            content += "<b>Confirm Regex: </b>" + confirm_regex + "<br />";
            content += "<b>Repair: </b>" + repair + "<br />";
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
    }
});

// show all rules
$("#show_all_rules").click(function () {

    $.get('rules/1', function (data) {
        $("#main-div").html(data);
    });

    make_rules_pagination(1);

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

            // post data
            var data = {
                'vul_type': vul_type,
                'language': lang,
                'regex': regex,
                'regex_confirm': regex_confirm,
                'description': description,
                'repair': repair
            };
            $.post('add_new_rule', data, function (res) {
                showAlert(res.tag, res.msg, '#add-new-rule-result');
            });
        });
    });
});

function make_vuls_pagination(cp) {
    // make pagination
    // get all rules count first
    var vuls_count = 0;
    var promise = $.ajax('all_vuls_count');
    promise.always(function (data) {
        vuls_count = data;
        var per_page_count = 10;
        var total_pages = Math.ceil(vuls_count / per_page_count);
        var current_page = cp;

        var pp = "<ul class='pagination'>";
        pp += "<li><a href='#' id='prev' role='button' class='btn' style='outline: none;' " +
            "onclick='prevVuls(" + current_page + ")'>Prev</a></li>";
        pp += "<li><a href='#' class='disabled'>" + current_page + " / " + total_pages + "</a></li>";
        pp += "<li><a href='#' id='next' role='button' class='btn' style='outline: none;' " +
            "onclick='nextVuls(" + current_page + "," + total_pages + ")'>Next</a></li>";
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

function prevVuls(cp) {
    if (cp <= 1) {
        $("#main-div").load('vuls/1');
    } else {
        $("#main-div").load('vuls/' + (cp-1));
    }
    make_vuls_pagination(cp-1);
}

function nextVuls(cp, tp) {
    if (cp >= tp) {
        $("#main-div").load('vuls/1');
    } else {
        $("#main-div").load('vuls/' + (cp+1));
    }
    make_vuls_pagination(cp+1);
}

// show all vuls
$("#show_all_vuls").click(function () {

    $.get('vuls/1', function (data) {
        $("#main-div").html(data);
    });

    make_vuls_pagination(1);
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

function make_projects_pagination(cp) {
    // make pagination
    // get all rules count first
    var projects_count = 0;
    var promise = $.ajax('all_projects_count');
    promise.always(function (data) {
        projects_count = data;
        var per_page_count = 10;
        var total_pages = Math.ceil(projects_count / per_page_count);
        var current_page = cp;

        var pp = "<ul class='pagination'>";
        pp += "<li><a href='#' id='prev' role='button' class='btn' style='outline: none;' " +
            "onclick='prevProjects(" + current_page + ")'>Prev</a></li>";
        pp += "<li><a href='#' class='disabled'>" + current_page + " / " + total_pages + "</a></li>";
        pp += "<li><a href='#' id='next' role='button' class='btn' style='outline: none;' " +
            "onclick='nextProjects(" + current_page + "," + total_pages + ")'>Next</a></li>";
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

function prevProjects(cp) {
    if (cp <= 1) {
        $("#main-div").load('projects/1');
    } else {
        $("#main-div").load('projects/' + (cp-1));
    }
    make_projects_pagination(cp-1);
}

function nextProjects(cp, tp) {
    if (cp >= tp) {
        $("#main-div").load('projects/1');
    } else {
        $("#main-div").load('projects/' + (cp+1));
    }
    make_projects_pagination(cp+1);
}

// show all projects click
$("#show_all_projects").click(function () {

    $.get('projects/1', function (data) {
        $("#main-div").html(data);
    });

    make_projects_pagination(1);
});

function make_whitelists_pagination(cp) {
    // make pagination
    // get all rules count first
    var projects_count = 0;
    var promise = $.ajax('all_whitelists_count');
    promise.always(function (data) {
        var whitelists_count = data;
        var per_page_count = 10;
        var total_pages = Math.ceil(whitelists_count / per_page_count);
        var current_page = cp;

        var pp = "<ul class='pagination'>";
        pp += "<li><a href='#' id='prev' role='button' class='btn' style='outline: none;' " +
            "onclick='prevWhitelsits(" + current_page + ")'>Prev</a></li>";
        pp += "<li><a href='#' class='disabled'>" + current_page + " / " + total_pages + "</a></li>";
        pp += "<li><a href='#' id='next' role='button' class='btn' style='outline: none;' " +
            "onclick='nextWhitelists(" + current_page + "," + total_pages + ")'>Next</a></li>";
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

function prevWhitelsits(cp) {
    if (cp <= 1) {
        $("#main-div").load('whitelists/1');
    } else {
        $("#main-div").load('whitelists/' + (cp-1));
    }
    make_whitelists_pagination(cp-1);
}

function nextWhitelists(cp, tp) {
    if (cp >= tp) {
        $("#main-div").load('whitelists/1');
    } else {
        $("#main-div").load('whitelists/' + (cp+1));
    }
    make_whitelists_pagination(cp+1);
}

// show all white lists click
$("#show_all_whitelists").click(function () {
    $.get('whitelists/1', function (data) {
        $("#main-div").html(data);
    });

    make_whitelists_pagination(1);
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
                showAlert('danger', 'project error.');
                return false;
            }

            if (!rule_id || rule_id == "") {
                showAlert('danger', 'rule error.');
                return false;
            }

            if (!path || path == "") {
                showAlert('danger', 'file cannot be empty.');
                return false;
            }

            if (!reason || reason == "") {
                showAlert('danger', 'reason can not be empty');
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
