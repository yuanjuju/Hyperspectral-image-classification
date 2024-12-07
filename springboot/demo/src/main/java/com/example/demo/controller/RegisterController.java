package com.example.demo.controller;

import com.aliyuncs.utils.StringUtils;
import com.example.demo.pojo.RegisterRequest;
import com.example.demo.pojo.Result;
import com.example.demo.service.SmsService;
import com.example.demo.service.StuService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Random;

@RestController
@RequestMapping("/api")
public class RegisterController {
    @Autowired
    private SmsService smsService;
    @Autowired
    private StuService stuService;
    @PostMapping("/send-register-code")
    public Result sendregistercode(@RequestBody String newPhone)
    {
        if (newPhone == null || !newPhone.matches("^[1][3-9][0-9]{9}$")) {
            return Result.error("手机号格式错误");
        }
        if (StringUtils.isEmpty(newPhone)) {
            return Result.error("短信发送失败");
        }
        String code = smsService.generateCode(newPhone);

        boolean success = smsService.sendCode(newPhone, code);
        if (success) {
            return Result.success("验证码短信发送成功");
        } else {
            return Result.success("验证码短信发送失败");
        }
    }
    @PostMapping("/register")
    public Result register(@RequestBody RegisterRequest registerRequest) {

        String phone = registerRequest.getPhone();
        String code = registerRequest.getCode();
        String password = registerRequest.getPassword();

        if (phone == null || code == null) {
            return Result.error("手机号和验证码不能为空");
        }

        // 验证验证码是否正确
        if (!smsService.verifyCode(phone, code)) {
            return Result.error("验证码错误或过期");
        }

        // 生成学号（格式：220+x（x为1-9）000+xxxx（x为1-9））
        String sno = generateStudentNumber();

        stuService.softinsert(sno,phone,password);

        if (true) {
            return Result.success(sno); // 返回生成的学号
        } else {
            return Result.error("注册失败，请重试");
        }
    }

    // 学号生成逻辑
    private String generateStudentNumber() {
        Random random = new Random();
        // 生成 x（1-9）的随机数字
        int x = random.nextInt(9) + 1;
        // 生成 000 + xxxx（x 为 1-9）的随机数字
        int suffix = random.nextInt(9000) + 1000;

        // 生成学号
        return "220" + x + "000" + suffix;
    }





}
