package com.example.demo.pojo;

import lombok.Data;

@Data
public class ChangePasswordBean {
    private String oldPassword;
    private String newPassword;
}
