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

var score2level = {
    1: 'Low',
    2: 'Low',
    3: 'Medium',
    4: 'Medium',
    5: 'Medium',
    6: 'High',
    7: 'High',
    8: 'High',
    9: 'Critical',
    10: 'Critical'
};


$(function () {
    var current_tab = '';
    var c_tab = getParameterByName('t');
    if (c_tab !== null && c_tab !== '' && ['inf', 'tar', 'fil','vul'].indexOf(c_tab) >= 0) {
        current_tab = c_tab;
        $(".nav-tabs li").removeClass('active');
        $("a[data-id=" + c_tab + "]").parent('li').addClass('active');
        $(".tab-pane").removeClass('active');
        $('#' + c_tab).addClass('active');
    }
    var vulnerabilities_list = {
        page: 1,
        vid: null,
        cm_code: null,
        init: function () {
            var vid = getParameterByName('vid');
            if (vid !== null && vid > 0) {
                vulnerabilities_list.vid = vid;
            }

            var s_sid = getParameterByName('s_sid');
            if (s_sid !== null) {
                $('#search_target').val(s_sid);
            }

            this.get();
            this.listen();
        },
        listen: function () {
            // filter submit button
            $('.filter_btn').on('click', function () {
                vulnerabilities_list.page = 1;
                vulnerabilities_list.pushState();
                vulnerabilities_list.get();
                vulnerabilities_list.trigger_filter();
            });

            // filter setting
            $('.filter_setting').on('click', function () {
                vulnerabilities_list.trigger_filter();
            });
        },
        detail: function (vid) {
            $('.vulnerabilities_list li').removeClass('active');
            $('li[data-id=' + vid + ']').addClass('active');
            vid = Number(vid);
            var sid = $('#search_target').val();
            var data = vul_list_origin.vulnerabilities[vid - 1];

            $.ajax({
                type: 'POST',
                url: '/api/detail',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify({sid: sid, file_path: data.file_path}),
                dataType: 'json',
                success: function (result) {
                    // hide loading
                    $('.CodeMirror .cm-loading').hide();
                    if (result.code === 1001) {
                        data.code_content = result.result.file_content;
                        data.language = result.result.extension;
                        // 对二进制文件情况进行处理，将行数置为 1
                        if (data.code_content === "This is a binary file.") {
                            data.line_number = 1;
                        }
                        $('#code').val(data.code_content);
                        // Highlighting param
                        vulnerabilities_list.cm_code.setOption("mode", data.language);
                        if (vulnerabilities_list.cm_code !== null) {
                            var doc = vulnerabilities_list.cm_code.getDoc();
                            doc.setValue(data.code_content);
                        }
                        vulnerabilities_list.cm_code.operation(function () {
                            // panel
                            $('.v-path').text(data.file_path + ':' + data.line_number);
                            $('.v-id').text('MVE-' + vid);
                            $('.v-language').text(data.language);

                            // widget
                            function init_widget() {
                                var lis = $('.widget-trigger li');
                                $('.commit-author').text('@' + data.commit_author);
                                $('.commit-time').text('@' + data.commit_time);
                                $('.v-level').text(score2level[data.level]);
                                $('.v-type').text('CVI-' + data.id + ' ' + data.rule_name);
                                $('.v-solution').text(data.solution);
                                // $('.v-rule').text(data.match_result);
                            }

                            init_widget();
                            var widget_trigger_line = $('.widget-trigger').clone().get(0);
                            var widget_config = {
                                coverGutter: false,
                                noHScroll: false
                            };
                            vulnerabilities_list.cm_code.addLineWidget(data.line_number - 1, widget_trigger_line, widget_config);
                            var h = vulnerabilities_list.cm_code.getScrollInfo().clientHeight;
                            var coords = vulnerabilities_list.cm_code.charCoords({
                                line: data.line_number,
                                ch: 0
                            }, "local");
                            vulnerabilities_list.cm_code.scrollTo(null, (coords.top + coords.bottom - h) / 2);
                            // set cursor
                            doc.setCursor({line: data.line_number - 1, ch: 0});

                        });

                        $('input[name=vulnerability_path]').val(data.file_path);
                        $('input[name=rule_id]').val(data.id);
                        $('input[name=vid]').val(data.id);

                        // vulnerabilities description
                        // $('.v_name').text(data.vulnerabilities.name);
                        // $('.v_score').text(data.vulnerabilities.score);
                        // $('.v_cwe').text(data.vulnerabilities.cwe);
                        // $('.v_owasp').text(data.vulnerabilities.owasp);
                        // $('.v_sana').text(data.vulnerabilities.sana);
                        // $('.v_bounty').text(data.vulnerabilities.bounty);
                    } else {
                        alert(result.msg);
                    }
                },
                error: function (result) {
                    alert('Fetch detail failed.');
                    $('.CodeMirror .cm-loading').hide();
                }
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

            var sid = '';
            if (sid !== null) {
                sid = '&sid=' + getParameterByName('sid');
            }

            var s_sid = '';
            if (s_sid !== null) {
                s_sid = '&s_sid=' + $('#search_target').val();
            }

            var url = '';
            if (current_tab === '' | current_tab === 'inf') {
                url = '?t=' + current_tab + sid + s_sid;
            } else if (current_tab === 'vul') {
                url = '?t=' + current_tab + sid + s_sid + vulnerabilities_list.filter_url() + v;
            } else if (current_tab === 'fil') {
                url = '?t=' + current_tab + sid + s_sid;
            } else if (current_tab === 'tar') {
                url = '?t=' + current_tab + sid + s_sid;
            }
            window.history.pushState("CobraState", "Cobra", url);
        },
        get: function (on_filter) {
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
                var content_top = '<strong class="v-path">/this/is/a/demo/code.php:1</strong>';
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

            vulnerabilities_list.pushState();

            // load vulnerabilities list

            $.ajax({
                type: 'POST',
                url: '/api/list',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify({sid: getParameterByName('s_sid')}),
                dataType: 'json',
                success: function (result) {
                    if (result.code === 1001) {
                        vul_list_origin = result.result.scan_data;
                        rule_filter = result.result.rule_filter;
                        // rule filter
                        $search_rule = $('#search_rule');
                        $search_rule.empty();
                        $search_rule.append('<option value="all">All</option>');
                        for (var key in rule_filter) {
                            $search_rule.append('<option value="' + key + '">' + rule_filter[key] + '</option>');
                        }

                        // Search vulnerability type
                        if (on_filter === false || typeof on_filter === 'undefined') {
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
                            // Search target
                            var st = getParameterByName('s_sid');
                            if (st !== null && st > 0) {
                                $('#search_target').val(st);
                            }
                        }

                        // vulnerabilities list
                        var list = vul_list_origin.vulnerabilities;
                        sl = Number(sl);
                        var list_html = '';

                        var id = 0;
                        for (var i = 0; i < list.length; i++) {
                            // search rule
                            if (sr !== null && sr > 0) {
                                if (list[i].id !== sr) {
                                    continue;
                                }
                            }
                            // search level
                            if (sl !== null && sl > 0) {
                                if (sl === 4) {
                                    if (list[i].level < 9) {
                                        continue;
                                    }
                                } else if (sl === 3) {
                                    if (list[i].level < 6 || list[i].level > 8) {
                                        continue;
                                    }
                                } else if (sl === 2) {
                                    if (list[i].level < 3 || list[i].level > 5) {
                                        continue;
                                    }
                                } else if (sl === 1) {
                                    if (list[i].level < 1 || list[i].level > 2) {
                                        continue;
                                    }
                                }
                            }
                            var line = '';
                            if (list[i].line_number !== 0) {
                                line = ':' + list[i].line_number;
                            }
                            list_html = list_html + '<li data-id="' + (i + 1) + '" class="' + score2level[list[i].level].toLowerCase() + '"' +
                                ' data-start="1" data-line="1">' +
                                '<strong>MVE-' + (i + 1) + '</strong><br><span>' + list[i].file_path + line + '</span><br>' +
                                '<span class="issue-information">' +
                                '<small>' + 'CVI-' + list[i].id +
                                ' => ' + list[i].rule_name +
                                '</small>' +
                                '</span>' +
                                '</li>';
                        }
                        if (list_html.length === 0) {
                            $(".vulnerabilities_list").html('<li><h3 style="text-align: center;margin: 200px auto;">Wow, no vulnerability was detected :)</h3></li>');
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
                    } else {
                        alert(result.msg);
                    }
                }
            });


        },
        trigger_filter: function () {
            if ($(".filter").is(":visible") === true) {
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
});
