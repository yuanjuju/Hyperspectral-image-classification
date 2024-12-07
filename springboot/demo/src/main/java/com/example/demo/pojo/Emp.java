package com.example.demo.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.security.PrivateKey;
import java.time.LocalDate;
import java.time.LocalDateTime;
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Emp {
    private Integer id;
    private String name;
    private String password;
    private String username;
    private String image;
    private Short gender;
    private String job;
    private Integer deptId;
    private LocalDate entryDate;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;


}
