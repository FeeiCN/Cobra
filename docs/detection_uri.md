## Introduction
先分析出项目所使用的框架，针对每个框架协商对应的规则来分析Model/View/Controller中的漏洞地址，并根据路由配置找出访问的URI。

# Detection CMS
针对每个框架的特征（文件或目录），来判断项目所使用的框架类型。
```
https://raw.githubusercontent.com/wufeifei/cobra/master/engine/detection.py
[
            {
                'name': 'Kohana',
                'site': 'http://kohanaframework.org/',
                'source': 'https://github.com/kohana/kohana',
                'rules': {
                    'directory': 'system/guide/kohana',
                    'file': 'system/config/userguide.php',
                },
                'public': 'public'
            },
            {
                'name': 'Laravel',
                'site': 'http://laravel.com/',
                'source': 'https://github.com/laravel/laravel',
                'rules': {
                    'file': 'artisan'
                }
            },
            {
                'name': 'ThinkPHP',
                'site': 'http://www.thinkphp.cn/',
                'source': 'https://github.com/top-think/thinkphp',
                'rules': {
                    'file': 'ThinkPHP/ThinkPHP.php'
                }
            },
            {
                'name': 'CodeIgniter',
                'site': 'https://codeigniter.com/',
                'source': 'https://github.com/bcit-ci/CodeIgniter',
                'rules': {
                    'file': 'system/core/CodeIgniter.php'
                }
            }
        ]
```

# Analyse CMS's route

TODO