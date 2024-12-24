package com.example.demo.controller;

import com.aliyuncs.utils.StringUtils;
import com.example.demo.pojo.*;
import com.example.demo.service.EmpService;
import com.example.demo.service.SmsService;
import com.example.demo.service.StuService;
import com.example.demo.utils.JwtUtils;
import com.example.demo.utils.SMSUtils;
import com.example.demo.utils.ValidateCodeUtils;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class LoginController {
    @Autowired
    private StuService stuService;
    @Autowired
    private SmsService smsService;

    @GetMapping("/test")
    public Result test() {
        return Result.success();
    }

//    @PostMapping("/login")
//    public Result login(@RequestBody Student student) {
//
//        System.out.println(student);
//        Student e = stuService.login(student);
//        if (e != null) {
//            Map<String, Object> claims = new HashMap<>();
//            claims.put("Sno", e.getSno());
//            claims.put("name", e.getSname());
//            claims.put("grade", e.getSgrade());
//            claims.put("profession", e.getSprofession());
//            String jwt = JwtUtils.generateJwt(claims);
//            return Result.success(jwt);
//        }
//        return Result.error("用户名或密码错误");
//    }

    @PostMapping("/login")
    public Result login(@RequestBody LoginBean loginBean) {
        String sno = loginBean.getSno();
        String password = loginBean.getPassword();
        String phone = loginBean.getPhone();
        String code = loginBean.getCode();

        if (sno != null && password != null) {
            Student e = stuService.login(sno, password);
            if (e != null) {
                Map<String, Object> claims = new HashMap<>();
                claims.put("Sno", e.getSno());
                claims.put("name", e.getSname());
                claims.put("grade", e.getSgrade());
                claims.put("profession", e.getSprofession());
                String jwt = JwtUtils.generateJwt(claims);
                return Result.success(jwt);
            }
            return Result.error("用户名或密码错误");
        } else if (phone != null && code != null) {
                // 验证验证码
                if (!smsService.verifyCode(phone, code)) {
                    return Result.error("验证码错误或过期");
                }

            Student e = stuService.getbyphone(phone);
            if (e != null) {
                Map<String, Object> claims = new HashMap<>();
                claims.put("Sno", e.getSno());
                claims.put("name", e.getSname());
                claims.put("grade", e.getSgrade());
                claims.put("profession", e.getSprofession());
                String jwt = JwtUtils.generateJwt(claims);
                return Result.success(jwt);
            }
            return Result.error("手机号错误");
            }
        else
        {
            return  Result.error("参数错误");
        }


    }

    @PostMapping("/send-code")
    public Result sendMsg(@RequestBody String phone) {
        System.out.println(phone);

        if (phone == null || !phone.matches("^[1][3-9][0-9]{9}$")) {
            return Result.error("手机号格式错误");
        }


        if (StringUtils.isEmpty(phone)) {
            return Result.error("短信发送失败");
        }
//      2.随机生成四位验证码
        String code = smsService.generateCode(phone);

        boolean success = smsService.sendCode(phone, code);
        if (success) {
            return Result.success("验证码短信发送成功");
        } else {
            return Result.success("验证码短信发送失败");
        }

    }
    @PostMapping("/verify-code")
    public Result verifyCode(@RequestBody LoginBean loginBean) {
        String phone = loginBean.getPhone();
        String code = loginBean.getCode();
        if (phone != null && code != null)
        {
            if (!smsService.verifyCode(phone, code)) {
                return Result.error("验证码错误或过期");
            }
            return Result.success();
        }
        else
            return Result.error("参数错误");
    }
    @PostMapping("/reset-password")
    public Result resetPassword(@RequestBody ResetPasswordBean passwordBean) {
        String phone = passwordBean.getPhone();
        String newPassword = passwordBean.getNewPassword();
        stuService.resetpassword(phone,newPassword);
        return Result.success();
    }


}






