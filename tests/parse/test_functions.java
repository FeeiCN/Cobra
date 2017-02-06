package com.feei.service.security.impl;

import com.feei.common.dto.Response;
import com.feei.service.security.dto.BlacklistDTO;
import com.feei.service.security.dto.BlacklistRespDTO;
import com.feei.service.security.entity.blacklist.BlacklistAllPool;
import com.feei.service.security.enums.BlacklistStatusEnum;
import com.feei.service.security.enums.BlacklistTypeEnum;
import com.feei.service.security.enums.ResultCodeEnum;
import com.feei.service.security.exception.ParamValidateException;
import com.feei.service.security.service.blacklist.Blacklist;
import com.feei.common.api.annotation.Public;
import org.springframework.stereotype.Service;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import javax.annotation.Resource;

@Public
@Service
public class BlacklistServiceImpl implements com.feei.service.security.api.BlacklistService {
    @Resource
    Blacklist blacklistService;

    // 可控
    private void sendGet() throws Exception {

        String url = "http://blog.feei.cn/ssrf";

        URL obj = new URL(url);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();

        // optional default is GET
        con.setRequestMethod("GET");

        //add request header
        con.setRequestProperty("User-Agent", USER_AGENT);

        int responseCode = con.getResponseCode();
        System.out.println("\nSending 'GET' request to URL : " + url);
        System.out.println("Response Code : " + responseCode);

        BufferedReader in = new BufferedReader(
                new InputStreamReader(con.getInputStream()));
        String inputLine;
        StringBuffer response = new StringBuffer();

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();

        //print result
        System.out.println(response.toString());

    }

    // 不可控, 已修复
    private void sendGet2() throws Exception {

        String url = req.getParameter("url");
        String url = Security.filter(url);
        URL obj = new URL(url);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();

        // optional default is GET
        con.setRequestMethod("GET");

        //add request header
        con.setRequestProperty("User-Agent", USER_AGENT);

        int responseCode = con.getResponseCode();
        System.out.println("\nSending 'GET' request to URL : " + url);
        System.out.println("Response Code : " + responseCode);

        BufferedReader in = new BufferedReader(
                new InputStreamReader(con.getInputStream()));
        String inputLine;
        StringBuffer response = new StringBuffer();

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();

        //print result
        System.out.println(response.toString());

    }


    @Override
    public Response<BlacklistRespDTO> inAll(BlacklistDTO blacklistDTO) {
        Response<BlacklistRespDTO> res = new Response<>();

        BlacklistRespDTO resp = new BlacklistRespDTO();

        try {
            Boolean inForceBindMobile     = blacklistService.in(blacklistDTO.getUserId(), BlacklistTypeEnum.FORCE_BIND_MOBILE.getDesc(), null);
            Boolean inForceModifyPassword = blacklistService.in(blacklistDTO.getUserId(), BlacklistTypeEnum.FORCE_MODIFY_PASSWORD.getDesc(), null);
            resp.setInForceBindMobile(inForceBindMobile);
            resp.setInForceModifyPassword(inForceModifyPassword);

            res.setData(resp);
            res.setCode(ResultCodeEnum.SUCCESS.getCode());
            res.setMessage(ResultCodeEnum.SUCCESS.getMessage());
        } catch (ParamValidateException e) {
            resp.setInForceModifyPassword(false);
            resp.setInForceBindMobile(false);
            res.setData(resp);
            res.setCode(e.getResultCodeEnum().getCode());
            res.setMessage(e.getResultCodeEnum().getMessage());
        }
        return res;
    }

    @Override
    public Response<Boolean> in(BlacklistDTO blacklistDTO) {
        Response<Boolean> res = new Response<>();

        try {
            if (blacklistDTO.getBusiness() == BlacklistTypeEnum.FORCE_MODIFY_PASSWORD.getValue() || blacklistDTO.getBusiness() == BlacklistTypeEnum.FORCE_BIND_MOBILE.getValue()) {
                BlacklistTypeEnum typeEnum;
                if (blacklistDTO.getBusiness() == BlacklistTypeEnum.FORCE_MODIFY_PASSWORD.getValue()) {
                    typeEnum = BlacklistTypeEnum.FORCE_MODIFY_PASSWORD;
                } else {
                    typeEnum = BlacklistTypeEnum.FORCE_BIND_MOBILE;
                }
                BlacklistAllPool blacklist = blacklistService.select(blacklistDTO.getUserId(), typeEnum.getDesc());
                if (blacklist == null) {
                    res.setData(false);
                } else {
                    if (blacklist.getStatus() == BlacklistStatusEnum.INIT.getValue()) {
                        if (blacklistDTO.getFrom() != null) {
                            if (blacklistDTO.getFrom().equals(blacklist.getExtra1())) {
                                res.setData(true);
                            } else {
                                res.setData(false);
                            }
                        } else {
                            res.setData(true);
                        }
                    } else {
                        res.setData(false);
                    }
                }

                res.setCode(ResultCodeEnum.SUCCESS.getCode());
                res.setMessage(ResultCodeEnum.SUCCESS.getMessage());
                return res;
            } else {
                res.setData(false);
                res.setCode(ResultCodeEnum.PARAM_EXCEPTION.getCode());
                res.setMessage(ResultCodeEnum.PARAM_EXCEPTION.getMessage());
                return res;
            }
        } catch (ParamValidateException e) {
            res.setData(false);
            res.setCode(e.getResultCodeEnum().getCode());
            res.setMessage(e.getResultCodeEnum().getMessage());
            return res;
        }
    }

    @Override
    public Response<String> up(BlacklistDTO blacklistDTO) {
        Response<String> res = new Response<>();

        res.setCode(ResultCodeEnum.SUCCESS.getCode());
        res.setMessage(ResultCodeEnum.SUCCESS.getMessage());
        res.setData("success up");

        return res;
    }

    @Override
    public Response<Boolean> add(BlacklistDTO blacklistDTO) {
        Response<Boolean> res = new Response<>();

        try {
            Boolean ret = blacklistService.add(blacklistDTO);

            res.setCode(ResultCodeEnum.SUCCESS.getCode());
            res.setMessage(ResultCodeEnum.SUCCESS.getMessage());
            res.setData(ret);
        } catch (ParamValidateException e) {
            res.setData(false);
            res.setCode(e.getResultCodeEnum().getCode());
            res.setMessage(e.getResultCodeEnum().getMessage());
            return res;
        }


        return res;
    }
}
