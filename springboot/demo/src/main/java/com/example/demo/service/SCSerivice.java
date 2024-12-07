package com.example.demo.service;

import com.example.demo.pojo.SC;

import java.util.List;

public interface SCSerivice {
    List<String> getbysno(String sno);

    void insert(String sno, String courseId,String coursename,Integer coursecredit,String coursesemester);

    void deleteCourse(String sno, String courseId);

    List<SC> getallmark(String sno);

    List<SC> getpartmark(String sno, String semester);
}
