package com.example.demo.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Course {
    private String Ccno;
    private String Cname;
    private String Ctime;
    private String Cdata;
    private String Cclassroom;
    private String Cteacher;
    private String Cdept;
    private Integer Ccapacity;
    private Integer Ccredit;
    private String Csemester;
    private String Cclass;
    private Integer Cduration;
}
