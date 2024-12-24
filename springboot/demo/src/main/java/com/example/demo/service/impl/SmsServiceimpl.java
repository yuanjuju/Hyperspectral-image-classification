package com.example.demo.service.impl;

import com.example.demo.service.SmsService;
import com.example.demo.utils.SMSUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Service
public class SmsServiceimpl  implements SmsService {
    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    public String generateCode(String phone) {
        String code = String.valueOf((int) ((Math.random() * 9 + 1) * 100000)); // 生成6位随机验证码
        redisTemplate.opsForValue().set(phone, code, 5, TimeUnit.MINUTES); // 设置5分钟有效期
        return code;
    }

    public boolean sendCode(String phone, String code) {
        SMSUtils.sendMessage("web课程设计", "SMS_475810055", phone, code);
        System.out.println("发送验证码: " + code + " 到手机号: " + phone);
        return true;
    }

    public boolean verifyCode(String phone, String code) {
        String cachedCode = redisTemplate.opsForValue().get(phone);
        return code != null && code.equals(cachedCode);
    }
}
