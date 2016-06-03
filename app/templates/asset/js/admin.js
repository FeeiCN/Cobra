/**
 * Created by lightless on 16/5/30.
 */


$("#main-div").fadeIn(1000);
function showAlert(tag, msg, div) {
    var tt = '<div class="alert alert-' + tag +' alert-dismissible" role="alert">';
    tt += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
    tt += '<span aria-hidden="true">&times;</span></button>';
    tt += '<strong>' + msg + '</strong></div>';
    $(div).html(tt).fadeIn(1000);
}

// show all rules
$("#show_all_rules").click(function () {
    $.get('rules', function (data) {
        $("#main-div").html(data);

        // delete the special rule
        $("[id^=del-rule]").click(function () {
            var cur_id = $(this).attr('id').split('-')[2];
            $.post('del_rule', {'rule_id':cur_id}, function (data) {
                var tt = '<div class="alert alert-' + data.tag +' alert-dismissible" role="alert">';
                tt += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                tt += '<span aria-hidden="true">&times;</span></button>';
                tt += '<strong>' + data.msg + '</strong></div>';
                $("#operate_result").html(tt).fadeIn(1000);
                $("#show_all_rules").click();
            });

        });

        // edit the special rule
        $("[id^=edit-rule]").click(function () {
            var cur_id = $(this).attr('id').split('-')[2];
            $.get('edit_rule/' + cur_id, function (result) {
                $('#main-div').html(result);

                $("#edit-rule-button").click(function () {
                    var vul_type = $("#vul_type").val();
                    var lang = $("#language").val();
                    var regex = $("#regex").val();
                    var description = $("#description").val();

                    // check data
                    if (!vul_type || vul_type == "") {
                        var result = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        result += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        result += '<span aria-hidden="true">&times;</span></button>';
                        result += '<strong>Vul type error.</strong></div>';
                        $("#add-new-rule-result").html(result).fadeIn(1000);
                        return false;
                    }
                    if (!lang || lang == "") {
                        var result = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        result += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        result += '<span aria-hidden="true">&times;</span></button>';
                        result += '<strong>Language error.</strong></div>';
                        $("#add-new-rule-result").html(result).fadeIn(1000);
                        return false;
                    }
                    if (!description || description == "") {
                        var result = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        result += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        result += '<span aria-hidden="true">&times;</span></button>';
                        result += '<strong>Description can not be blank.</strong></div>';
                        $("#add-new-rule-result").html(result).fadeIn(1000);
                        return false;
                    }
                    if (!regex || regex == "") {
                        var result = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        result += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        result += '<span aria-hidden="true">&times;</span></button>';
                        result += '<strong>regex can not be blank.</strong></div>';
                        $("#add-new-rule-result").html(result).fadeIn(1000);
                        return false;
                    }

                    // post data
                    var data = {
                        'vul_type': vul_type,
                        'language': lang,
                        'regex': regex,
                        'description': description,
                        'rule_id': cur_id
                    };
                    $.post('edit_rule/' + cur_id, data, function (res) {
                        var tres = '<div class="alert alert-' + res.tag + ' alert-dismissible" role="alert">';
                        tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        tres += '<span aria-hidden="true">&times;</span></button>';
                        tres += '<strong>' + res.msg + '</strong></div>';
                        $("#edit-rule-result").html(tres).fadeIn(1000);
                    });
                });
            });
        });

        // view the special rule
        $("[id^=view-rule]").click(function () {
            var cur_id = $(this).attr('id').split('-')[2];
            var regex = $("<div/>").text($("#rule-regex-" + cur_id).text()).html();
            var confirm_regex = $("<div/>").text($("#rule-confirm-regex-" + cur_id).text()).html();
            var repair = $("<div/>").text($("#rule-repair-" + cur_id).text()).html();
            $("#view-title").html("Rule Details.");
            var content = "<b>Regex: </b>" + regex + "<br />";
            content += "<b>Confirm Regex: </b>" + confirm_regex + "<br />";
            content += "<b>Repair: </b>" + repair + "<br />";
            $("#view-body").html(content);
        });

    });
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

// show all vuls
$("#show_all_vuls").click(function () {
    $.get('vuls', function (data) {
        $("#main-div").html(data);

        // delete the special vul
        $("[id^=del-vul]").click(function () {
            var current_id = $(this).attr('id');
            var vul_id = current_id.split('-')[2];

            $.post('del_vul', {'vul_id':vul_id}, function (result) {
                var tt = '<div class="alert alert-' + result.tag +' alert-dismissible" role="alert">';
                tt += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                tt += '<span aria-hidden="true">&times;</span></button>';
                tt += '<strong>' + result.msg + '</strong></div>';
                $("#operate_result").html(tt).fadeIn(1000);
                $("#show_all_vuls").click();
            });
        });

        // edit the special vul
        $("[id^=edit-vul]").click(function () {
            var current_id = $(this).attr('id');
            var vul_id = current_id.split('-')[2];

            $.get('edit_vul/'+vul_id, function (data) {
                $("#main-div").html(data);

                $("#edit-vul-button").click(function () {
                    var name = $("#name").val();
                    var description = $("#description").val();
                    if (!name || !description || name == "" || description == "") {
                        var result = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        result += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        result += '<span aria-hidden="true">&times;</span></button>';
                        result += '<strong>name or description can not be empty!</strong></div>';
                        $("#edit-vul-result").html(result).fadeIn(1000);
                        return false;
                    }
                    data = {
                        'vul_id': vul_id,
                        'name': name,
                        'description': description
                    };
                    $.post('edit_vul/' + vul_id, data, function (res) {
                        var tres = '<div class="alert alert-' + res.tag + ' alert-dismissible" role="alert">';
                        tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        tres += '<span aria-hidden="true">&times;</span></button>';
                        tres += '<strong>' + res.msg + '</strong></div>';
                        $("#edit-vul-result").html(tres).fadeIn(1000);
                    });
                });
            });
        });
    });
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
            var result = '';
            if (name == "" || !name) {
                result += '<div class="alert alert-danger alert-dismissible" role="alert">';
                result += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                result += '<span aria-hidden="true">&times;</span></button>';
                result += '<strong>name is empty!</strong></div>';
                $("#add-new-vul-result").html(result).fadeIn(1000);
                return false;
            }
            if (description == "" || !description) {
                result += '<div class="alert alert-danger alert-dismissible" role="alert">';
                result += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                result += '<span aria-hidden="true">&times;</span></button>';
                result += '<strong>description is empty!</strong></div>';
                $("#add-new-vul-result").html(result).fadeIn(1000);
                return false;
            }
            var data = {
                'name': name,
                'description': description
            };
            $.post('add_new_vul', data, function (res) {
                var tres = '<div class="alert alert-' + res.tag + ' alert-dismissible" role="alert">';
                tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                tres += '<span aria-hidden="true">&times;</span></button>';
                tres += '<strong>' + res.msg + '</strong></div>';
                $("#add-new-vul-result").html(tres).fadeIn(1000);
            });
        });
    });
});


// show all projects click
$("#show_all_projects").click(function () {
    $.get('projects', function (data) {
        $("#main-div").html(data);

        // edit project click
        $("[id^=edit-project]").click(function () {
            var cur_project_id = $(this).attr('id');
            cur_project_id = cur_project_id.split('-')[2];
            $.get("edit_project/"+cur_project_id, function (data) {
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
                        'project_id': cur_project_id,
                        'name': name,
                        'repository' : repository,
                        'author': author,
                        'remark': remark
                    };
                    $.post('edit_project/'+cur_project_id, data, function (res) {
                        showAlert(res.tag, res.msg, '#edit-project-result');
                    });
                });
            });
        });

        // view project click
        $("[id^=view-project]").click(function () {
            var cur_project_id = $(this).attr('id').split('-')[2];
        });

        // delete project click
        $("[id^=del-project]").click(function () {
            var cur_project_id = $(this).attr('id');
            cur_project_id = cur_project_id.split('-')[2];
            
            $.post("del_project", {"id":cur_project_id}, function (result) {
                var tt = '<div class="alert alert-' + result.tag +' alert-dismissible" role="alert">';
                tt += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                tt += '<span aria-hidden="true">&times;</span></button>';
                tt += '<strong>' + result.msg + '</strong></div>';
                $("#operate_result").html(tt).fadeIn(1000);
            });
            $("#show_all_projects").click();
        });

    });
});


// show all white lists click
$("#show_all_whitelists").click(function () {
    $.get('whitelists', function (data) {
        $("#main-div").html(data);

        // edit the special white list
        $("[id^=edit-whitelist]").click(function () {
            var cur_id = $(this).attr('id').split('-')[2];
            console.log("edit the " + cur_id);

            $.get('edit_whitelist/'+cur_id, function (data) {
                $("#main-div").html(data);

                $("#edit-whitelist-button").click(function () {
                    var project = $("#project").val();
                    var rule = $("#rule").val();
                    var path = $("#path").val();
                    var reason = $("#reason").val();
                    var status = $("#status:checked").val();

                    data = {
                        'whitelist_id': cur_id,
                        'project': project,
                        'rule': rule,
                        'path': path,
                        'reason': reason,
                        'status': status
                    };

                    $.post("edit_whitelist/"+cur_id, data, function (result) {
                        showAlert(result.tag, result.msg, '#edit-whitelist-result');
                    });
                });
            });
        });


        // delete the special white list
        $("[id^=del-whitelist]").click(function () {
            var cur_id = $(this).attr('id').split('-')[2];
            $.post('del_whitelist', {'whitelist_id': cur_id}, function (data) {
                showAlert(data.tag, data.msg, "#operate_result");
                $("#show_all_whitelists").click();
            });
        });


    });
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
