/**
 * Created by lightless on 16/5/30.
 */


$("#main-div").fadeIn(1000);

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
            $("#view-title").html("Rule Details.");
            $("#view-body").html("<b>Regex in Perl: </b>" + regex);
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
                'description': description
            };
            $.post('add_new_rule', data, function (res) {
                var tres = '<div class="alert alert-' + res.tag + ' alert-dismissible" role="alert">';
                tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                tres += '<span aria-hidden="true">&times;</span></button>';
                tres += '<strong>' + res.msg + '</strong></div>';
                $("#add-new-rule-result").html(tres).fadeIn(1000);
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
                    var repo_type = $("input[name=repo_type]:checked").val();
                    var repository = $("#repository").val();
                    var branch = $("#branch").val();
                    var username = $("#username").val();
                    var password = $("#password").val();

                    if (!name || name == "") {
                        var tres = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        tres += '<span aria-hidden="true">&times;</span></button>';
                        tres += '<strong>name cannot be empty!</strong></div>';
                        $("#edit-project-result").html(tres).fadeIn(1000);
                    }

                    if (!repo_type || repo_type == "") {
                        var tres = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        tres += '<span aria-hidden="true">&times;</span></button>';
                        tres += '<strong>repo type error.</strong></div>';
                        $("#edit-project-result").html(tres).fadeIn(1000);
                    }

                    if (!repository || repository == "") {
                        var tres = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        tres += '<span aria-hidden="true">&times;</span></button>';
                        tres += '<strong>repository cannot be empty!</strong></div>';
                        $("#edit-project-result").html(tres).fadeIn(1000);
                    }

                    if (!branch || branch == "") {
                        var tres = '<div class="alert alert-danger alert-dismissible" role="alert">';
                        tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        tres += '<span aria-hidden="true">&times;</span></button>';
                        tres += '<strong>branch cannot be empty!</strong></div>';
                        $("#edit-project-result").html(tres).fadeIn(1000);
                    }

                    data = {
                        'project_id': cur_project_id,
                        'name': name,
                        'repo_type': repo_type,
                        'repository' : repository,
                        'branch' : branch,
                        'username': username,
                        'password': password
                    };
                    $.post('edit_project/'+cur_project_id, data, function (res) {
                        var tres = '<div class="alert alert-' + res.tag + ' alert-dismissible" role="alert">';
                        tres += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                        tres += '<span aria-hidden="true">&times;</span></button>';
                        tres += '<strong>' + res.msg + '</strong></div>';
                        $("#edit-project-result").html(tres).fadeIn(1000);
                    });

                });


            });
        });

        // view project click

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
    console.log('show all white list');
});
