package com.example.demo.service;

import com.example.demo.pojo.Course;

import java.util.List;

public interface CourseService {
    Course getbycno(String cno);

    List<Course> getcourseinfo();

    List<Course> GetGyTypeandMajor(String courseType, String major);
}
