package com.example.demo.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;



@Data
@AllArgsConstructor
@NoArgsConstructor
public class Student {
    private String sno;
    private String Sname;
    private Integer Sage;
    private String Sgrade;
    private String Sprofession;
    private String password;
    private String Sdept;
    private String Sidentity;
    private String Sphone;
    private String Semail;

}
