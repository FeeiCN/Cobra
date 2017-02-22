$(function () {
    var vulnerabilities_list = {
        page: 1,
        init: function () {
            this.get();
            this.listen();
        },
        listen: function () {
            // filter submit button
            $('.filter_btn').on('click', function () {
                vulnerabilities_list.page = 1;
                vulnerabilities_list.get();
                vulnerabilities_list.trigger_filter();
            });

            // filter setting
            $('.filter_setting').on('click', function () {
                vulnerabilities_list.trigger_filter();
            });

            // scroll load
            $(".vulnerabilities_list").scroll(function () {
                if ($(".vulnerabilities_list").scrollTop() > 300 * vulnerabilities_list.page) {
                    vulnerabilities_list.next_page();
                }
            });

            // mistake
            $('button.mistake').on('click', function () {
                if (window.confirm('Add white-list for the vulnerability?')) {
                    var rule_id = $('input[name=rule_id]').val();
                    if (rule_id == '') {
                        alert('Select list of vulnerability!');
                        return;
                    }
                    var reason = window.prompt('Why add white-list?');
                    if (reason == '') {
                        alert('Add white-list reason can\'t empty!');
                        return;
                    }
                    var data = {
                        'project': $('input[name=project_id]').val(),
                        'rule': rule_id,
                        'path': $('input[name=vulnerability_path]').val(),
                        'reason': reason,
                        'status': 1
                    };
                    $.post('/admin/white-list/create/', data, function (ret) {
                        if (ret.code == 1001) {
                            alert(ret.message);
                        } else {
                            alert(ret.message);
                        }
                    }, 'JSON');
                }
            });

            // delete
            $('button.delete').on('click', function () {
                var vid = $('input[name=vid]').val();
                if (vid == "") {
                    alert("Select vulnerability on the left");
                    return;
                }
                if (window.confirm('Are you sure you want to remove this vulnerability?')) {
                    var data = {
                        'vid': vid
                    };
                    $.post('/admin/vulnerability/delete/', data, function (ret) {
                        if (ret.code == 1001) {
                            alert(ret.message);
                        } else {
                            alert(ret.message);
                        }
                    }, 'JSON');
                }
            });
        },
        next_page: function () {
            this.page = this.page + 1;
            this.get(true);
        },
        cm_code: null,
        get: function (next_page) {
            if ($("input[name=need_scan]").val() != "False") {
                // load vulnerabilities list
                $.post('/list', {
                    project_id: $('input[name=project_id]').val(),
                    page: this.page,
                    search_vul_type: $("#search_vul_type").val(),
                    search_rule: $("#search_rule").val(),
                    search_level: $("#search_level").val(),
                    search_task: $("#search_task").val(),
                    search_status: $("#search_status").val()
                }, function (result) {
                    if (result.status_code == 1001) {
                        var list = result.data.vulnerabilities;
                        if (result.data.current_page == 1 && list.length == 0) {
                            $(".vulnerabilities_list").html('<li><h3 style="text-align: center;margin: 200px auto;">Wow, no vulnerability was detected :)</h3></li>');
                        } else {
                            var list_html = '';

                            for (var i = 0; i < list.length; i++) {
                                var line = '';
                                if (list[i].line != 0) {
                                    line = ':' + list[i].line;
                                }
                                list_html = list_html + '<li data-id="' + list[i].id + '" class="' + list[i].color + ' ' + list[i].status_class + '" data-start="1" data-line="1">' +
                                    '<strong>MVE-' + list[i].id + '</strong><br><span>' + list[i].file_short + line + '</span><br>' +
                                    '<span class="issue-information">' +
                                    '<small>' +
                                    list[i].v_name + ' => ' + list[i].rule +
                                    '</small>' +
                                    '</span>' +
                                    '</li>';
                            }
                            if (next_page) {
                                $('.vulnerabilities_list').append(list_html);
                            } else {
                                $('.vulnerabilities_list').html(list_html);
                            }

                            // vulnerabilities list detail
                            $('.vulnerabilities_list li').off('click').on('click', function () {
                                $('.vulnerabilities_list li').removeClass('active');
                                $(this).addClass('active');
                                var id = $(this).attr('data-id');
                                $.post('/detail', {id: id}, function (result) {
                                    if (result.status_code == 1001) {
                                        var data = result.data;
                                        $('#code').val(data.detail.code);
                                        // vulnerabilities code
                                        if (vulnerabilities_list.cm_code == null) {
                                            vulnerabilities_list.cm_code = CodeMirror.fromTextArea(document.getElementById("code"), {
                                                mode: 'php',
                                                theme: 'material',
                                                lineNumbers: true,
                                                lineWrapping: true,
                                                matchBrackets: true,
                                                matchTags: {bothTags: true},
                                                indentUnit: 4,
                                                indentWithTabs: true,
                                                foldGutter: true,
                                                scrollbarStyle: 'simple',
                                                autofocus: false,
                                                readOnly: true,
                                                highlightSelectionMatches: {showToken: /\w/, annotateScrollbar: true},
                                                gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"]
                                            });

                                            // fullscreen
                                            // cm.setOption("fullScreen", !cm.getOption("fullScreen"));
                                            // if (cm.getOption("fullScreen")) cm.setOption("fullScreen", false);

                                            // panel
                                            var numPanels = 0;
                                            var panels = {};

                                            function makePanel(where, content) {
                                                var node = document.createElement("div");
                                                var id = ++numPanels;
                                                var widget;
                                                node.id = "panel-" + id;
                                                node.className = "cm_panel widget-" + where;
                                                node.innerHTML = content;
                                                return node;
                                            }

                                            function addPanel(where, content) {
                                                var node = makePanel(where, content);
                                                panels[node.id] = vulnerabilities_list.cm_code.addPanel(node, {position: where, stable: true});
                                            }

                                            var content_bottom = 'MVE-' + ' ' + data.detail.id + ' ' + data.detail.created + '<span> ' + data.rule.language + '</span>';
                                            addPanel('bottom', content_bottom);
                                            var content_top = '<strong>' + data.detail.file + ':' + (data.detail.line_start + data.detail.line_trigger - 1) + '</strong>';
                                            addPanel('top', content_top);
                                        } else {
                                            var doc = vulnerabilities_list.cm_code.getDoc();
                                            doc.setValue(data.detail.code);
                                        }

                                        vulnerabilities_list.cm_code.operation(function () {
                                            // widget
                                            function init_widget() {
                                                var lis = $('.widget-trigger li');
                                                $('.commit-author').text('@' + data.detail.c_author);
                                                $('.commit-time').text('@' + data.detail.c_time);
                                                $('.v-status').text(data.detail.status);
                                                $('.v-level').text(data.rule.level);
                                                $('.v-type').text(data.description.name);
                                                $('.v-rule').text(data.rule.description);
                                                $('.v-rule-author').text('@' + data.rule.author);
                                                $('.v-repair-time').text(data.detail.updated);
                                                $('.v-repair-description').text(data.rule.repair);
                                            }

                                            init_widget();
                                            var widget_trigger_line = $('.widget-trigger').clone().get(0);
                                            var widget_config = {
                                                coverGutter: true,
                                                noHScroll: true
                                            };
                                            vulnerabilities_list.cm_code.addLineWidget(data.detail.line_trigger - 1, widget_trigger_line, widget_config);
                                            var after = vulnerabilities_list.cm_code.charCoords({line: vulnerabilities_list.cm_code.getCursor().line + 1, ch: 0}, "isEmpty").top;
                                            vulnerabilities_list.cm_code.scrollTo(null, after);
                                        });

                                        $('input[name=vulnerability_path]').val(data.detail.file);
                                        $('input[name=rule_id]').val(data.rule.id);
                                        $('input[name=vid]').val(data.detail.id);

                                        // vulnerabilities description
                                        // $('.v_name').text(data.vulnerabilities.name);
                                        // $('.v_score').text(data.vulnerabilities.score);
                                        // $('.v_cwe').text(data.vulnerabilities.cwe);
                                        // $('.v_owasp').text(data.vulnerabilities.owasp);
                                        // $('.v_sana').text(data.vulnerabilities.sana);
                                        // $('.v_bounty').text(data.vulnerabilities.bounty);
                                    } else {
                                        alert(result.message);
                                    }
                                }, 'JSON');
                            });
                        }
                    } else {
                        alert(result.message);
                    }
                }, 'JSON');
            } else {
                $(".vulnerabilities_list").html('<li><h3 style="text-align: center;margin: 200px auto;">The project is deprecated :(</h3></li>');
            }
        },
        trigger_filter: function () {
            if ($(".filter").is(":visible") == true) {
                $('.filter').hide();
                $('.vulnerabilities_list').show();
            } else {
                $('.vulnerabilities_list').hide();
                $('.filter').show();
            }

        }
    };

    vulnerabilities_list.init();


    // nav
    $(".nav-tabs li a").on('click', function () {
        var id = $(this).attr('data-id');
        $(".nav-tabs li").removeClass('active');
        $(this).parent('li').addClass('active');
        $(".tab-pane").removeClass('active');
        $('#' + id).addClass('active');
    });

    $('.icon_set_1_icon-74').click(function () {
        var rule_id = $(this).attr('rule_id');
        var project_path = $(this).attr('file_path');
        var project_id = $('input[name=project_id]').val();
        var data = {'project_id': project_id, 'rule_id': rule_id, 'path': project_path, 'reason': 'Remark'};
        $.ajax({
            'url': '/admin/add_whitelist',
            'type': 'POST',
            'data': data,
            //'contentType':'application/json; charset=utf-8',
            'async': false,
            'success': function (result) {
                if (result.tag == 'success') {
                    alert('Add whitelist success!');
                }
            }
        });
    });

    /* Ext Chart */
    var ext_distributing = echarts.init(document.getElementById('ext_distributing'));
    ext_distributing.showLoading();

    var task_id = $('input[name=task_id]').val();
    $.get('/ext/' + task_id, function (result) {
        if (result.code == 1001) {
            var diskData = result.result;
            ext_distributing.hideLoading();

            function colorMappingChange(value) {
                var levelOption = getLevelOption(value);
                chart.setOption({
                    series: [{
                        levels: levelOption
                    }]
                });
            }

            var formatUtil = echarts.format;

            function getLevelOption() {
                return [
                    {
                        itemStyle: {
                            normal: {
                                borderWidth: 0,
                                gapWidth: 5
                            }
                        }
                    },
                    {
                        itemStyle: {
                            normal: {
                                gapWidth: 1
                            }
                        }
                    },
                    {
                        colorSaturation: [0.35, 0.5],
                        itemStyle: {
                            normal: {
                                gapWidth: 1,
                                borderColorSaturation: 0.6
                            }
                        }
                    }
                ];
            }

            ext_distributing.setOption(option = {
                tooltip: {
                    formatter: function (info) {
                        var value = info.value;
                        var treePathInfo = info.treePathInfo;
                        var treePath = [];

                        for (var i = 1; i < treePathInfo.length; i++) {
                            treePath.push(treePathInfo[i].name);
                        }

                        return [
                            '<div class="tooltip-title">' + formatUtil.encodeHTML(treePath.join('/')) + '</div>',
                            'Amount: ' + formatUtil.addCommas(value),
                        ].join('');
                    }
                },

                series: [
                    {
                        name: 'Ext',
                        type: 'treemap',
                        roam: false,
                        visibleMin: 300,
                        label: {
                            show: true,
                            formatter: '{b}'
                        },
                        itemStyle: {
                            normal: {
                                borderColor: '#fff'
                            }
                        },
                        levels: getLevelOption(),
                        data: diskData
                    }
                ]
            });
        } else {
            alert(result.result);
        }
    }, 'JSON');
});
