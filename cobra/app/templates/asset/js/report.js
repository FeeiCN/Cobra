function getParameterByName(name, url) {
    if (!url) {
        url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}
$(function () {
    var current_tab = '';
    var c_tab = getParameterByName('t');
    if (c_tab !== null && c_tab !== '' && ['inf', 'vul', 'ext'].indexOf(c_tab) >= 0) {
        current_tab = c_tab;
        $(".nav-tabs li").removeClass('active');
        $("a[data-id=" + c_tab + "]").parent('li').addClass('active');
        $(".tab-pane").removeClass('active');
        $('#' + c_tab).addClass('active');
    }
    var vulnerabilities_list = {
        page: 1,
        vid: null,
        init: function () {
            var vid = getParameterByName('vid');
            if (vid !== null && vid > 0) {
                vulnerabilities_list.vid = vid;
            }
            this.get();
            this.listen();
        },
        listen: function () {
            // filter submit button
            $('.filter_btn').on('click', function () {
                vulnerabilities_list.page = 1;
                vulnerabilities_list.get(false, true);
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
        },
        next_page: function () {
            this.page = this.page + 1;
            this.get(true);
        },
        cm_code: null,
        detail: function (vid) {
            $('.vulnerabilities_list li').removeClass('active');
            $('li[data-id=' + vid + ']').addClass('active');
            $.post('/detail', {id: vid}, function (result) {
                // hide loading
                $('.CodeMirror .cm-loading').hide();
                if (result.status_code == 1001) {
                    var data = result.data;
                    $('#code').val(data.detail.code);
                    // Highlighting param
                    vulnerabilities_list.cm_code.setOption("mode", data.detail.mode);
                    if (vulnerabilities_list.cm_code !== null) {
                        var doc = vulnerabilities_list.cm_code.getDoc();
                        doc.setValue(data.detail.code);
                    }
                    vulnerabilities_list.cm_code.operation(function () {
                        // panel
                        $('.v-path').text(data.detail.file + ':' + data.detail.line_trigger);
                        $('.v-id').text('MVE-' + data.detail.id);
                        $('.v-language').text(data.rule.language);
                        // widget
                        function init_widget() {
                            var lis = $('.widget-trigger li');
                            $('.commit-author').text('@' + data.detail.c_author);
                            $('.commit-time').text('@' + data.detail.c_time);
                            $('.v-status').text(data.detail.status);
                            $('.v-repair').text(data.detail.repair);
                            $('.v-level').text(data.rule.level);
                            $('.v-type').text(data.description.name);
                            $('.v-rule').text(data.rule.description);
                            $('.v-rule-author').text('@' + data.rule.author);
                            $('.v-repair-time').text(data.detail.updated);
                            $('.v-repair-description').html(data.rule.repair);
                        }

                        init_widget();
                        var widget_trigger_line = $('.widget-trigger').clone().get(0);
                        var widget_config = {
                            coverGutter: false,
                            noHScroll: false
                        };
                        vulnerabilities_list.cm_code.addLineWidget(data.detail.line_trigger - 1, widget_trigger_line, widget_config);
                        var h = vulnerabilities_list.cm_code.getScrollInfo().clientHeight;
                        var coords = vulnerabilities_list.cm_code.charCoords({line: data.detail.line_trigger, ch: 0}, "local");
                        vulnerabilities_list.cm_code.scrollTo(null, (coords.top + coords.bottom - h) / 2);
                        // set cursor
                        doc.setCursor({line: data.detail.line_trigger - 1, ch: 0});

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
            }, 'JSON').fail(function (response) {
                alert('Backend service failed, try again later!');
                // hide loading
                $('.CodeMirror .cm-loading').hide();
            });
        },
        filter_url: function () {
            var search_filter_url = '';
            var svt = $('#search_vul_type').val();
            if (svt !== 'all' && svt > 0) {
                search_filter_url += '&svt=' + svt;
            }
            var sr = $('#search_rule').val();
            if (sr !== 'all' && sr > 0) {
                search_filter_url += '&sr=' + sr;
            }
            var sl = $('#search_level').val();
            if (sl !== 'all' && sl > 0) {
                search_filter_url += '&sl=' + sl;
            }
            var st = $('#search_task').val();
            if (st !== 'all' && st > 0) {
                search_filter_url += '&st=' + st;
            }
            var ss = $('#search_status').val();
            if (ss > 0) {
                search_filter_url += '&ss=' + ss;
            }
            return search_filter_url;
        },
        pushState: function () {
            var v = '';
            if (vulnerabilities_list.vid !== null) {
                v = '&vid=' + vulnerabilities_list.vid;
            }
            var url = '';
            if (current_tab === '' || current_tab === 'inf') {
                url = '?t=' + 'inf';
            } else {
                if (current_tab === 'vul') {
                    url = "?t=" + current_tab + vulnerabilities_list.filter_url() + v;
                } else {
                    url = '?t=' + 'ext';
                }
            }
            window.history.pushState("CobraState", "Cobra", url);
        },
        get: function (next_page, on_filter) {
            // vulnerabilities code
            if (vulnerabilities_list.cm_code === null) {
                vulnerabilities_list.cm_code = CodeMirror.fromTextArea(document.getElementById("code"), {
                    mode: 'php',
                    theme: 'material',
                    lineNumbers: true,
                    lineWrapping: true,
                    matchBrackets: true,
                    styleActiveLine: true,
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

                var content_bottom = '<span class="v-id">MVE-0001</span>' + '<span class="v-language">PHP</span>';
                addPanel('bottom', content_bottom);
                var content_top = '<strong class="v-path">/this/is/a/demo/code.php:1</strong><img class="icon full-screen" src="/asset/icon/resize-full-screen.png" alt="Full screen">';
                addPanel('top', content_top);

                // full screen
                $('.full-screen').click(function () {
                    $('.exit-full-screen').show();
                    vulnerabilities_list.cm_code.setOption("fullScreen", !vulnerabilities_list.cm_code.getOption("fullScreen"));
                });
                $('.exit-full-screen').click(function () {
                    $('.exit-full-screen').hide();
                    if (vulnerabilities_list.cm_code.getOption("fullScreen")) vulnerabilities_list.cm_code.setOption("fullScreen", false);
                });

                // ESC exit full screen
                $('body').on('keydown', function (evt) {
                    if (evt.keyCode === 27) {
                        if (vulnerabilities_list.cm_code.getOption("fullScreen")) vulnerabilities_list.cm_code.setOption("fullScreen", false);
                    }
                    evt.stopPropagation();
                });
            }
            if ($("input[name=need_scan]").val() !== "False") {
                // Search vulnerability type
                if (on_filter === false || typeof on_filter === 'undefined') {
                    var svt = getParameterByName('svt');
                    if (svt !== null && svt > 0) {
                        $('#search_vul_type').val(svt);
                    }
                    // Search rule
                    var sr = getParameterByName('sr');
                    if (sr !== null && sr > 0) {
                        $('#search_rule').val(sr);
                    }
                    // Search level
                    var sl = getParameterByName('sl');
                    if (sl !== null && sl > 0) {
                        $('#search_level').val(sl);
                    }
                    // Search task
                    var st = getParameterByName('st');
                    if (st !== null && st > 0) {
                        $('#search_task').val(st);
                    }
                    // Search status
                    var ss = getParameterByName('ss');
                    if (ss !== null && ss > 0) {
                        $('#search_status').val(ss);
                    }
                }

                vulnerabilities_list.pushState();

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

                            // current vulnerability
                            var vid = getParameterByName('vid');
                            if (vid !== null && vid > 0) {
                                vulnerabilities_list.detail(vid);
                            }

                            // vulnerabilities list detail
                            $('.vulnerabilities_list li').off('click').on('click', function () {
                                // loading
                                $('.CodeMirror').prepend($('.cm-loading').show().get(0));

                                vulnerabilities_list.vid = $(this).attr('data-id');

                                vulnerabilities_list.pushState();
                                vulnerabilities_list.detail(vulnerabilities_list.vid);
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


    // tab
    $(".nav-tabs li a").on('click', function () {
        var id = $(this).attr('data-id');
        current_tab = id;
        $(".nav-tabs li").removeClass('active');
        $(this).parent('li').addClass('active');
        $(".tab-pane").removeClass('active');
        $('#' + id).addClass('active');
        vulnerabilities_list.pushState();
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
