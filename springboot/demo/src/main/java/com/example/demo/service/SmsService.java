package com.example.demo.service;

public interface SmsService {
    public String generateCode(String phone);
    public boolean sendCode(String phone, String code);
    public boolean verifyCode(String phone, String code);
}
