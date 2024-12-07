package com.example.demo.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class SC {
    private String Sno;
    private String Cno;
    private String name;
    private Integer mark;
    private Integer credit;
    private String semester;
}
