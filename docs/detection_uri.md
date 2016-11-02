# Introduction
First analyze the framework used by the project, analyze the vulnerability address in Model / View / Controller according to the corresponding rules of each frame negotiation, and find out the accessed URI according to the routing configuration.

# Detection CMS
For each frame's characteristics (files or directories), determine the frame type used by the project.
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