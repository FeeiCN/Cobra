-- author:JoyChou(viarus@qq.com)
-- date:2017.08.01

-- CVI-140004
ngx.header.content_type = "text/html"
ngx.say(ngx.req.get_uri_args().name)
