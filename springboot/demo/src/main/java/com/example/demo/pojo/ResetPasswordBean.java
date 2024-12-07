package com.example.demo.pojo;

import lombok.Data;

@Data
public class ResetPasswordBean {
    private String phone;
    private String newPassword;
}
