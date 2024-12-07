package com.example.demo.service.impl;

import com.example.demo.mapper.CourseMapper;
import com.example.demo.pojo.Course;
import com.example.demo.service.CourseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CourseServiceimpl implements CourseService {
    @Autowired
    private CourseMapper courseMapper;
    @Override
    public Course getbycno(String cno)
    {
        return courseMapper.getbycno(cno);
    }


    @Override
    public List<Course> getcourseinfo()
    {
        return courseMapper.getcourseinfo();
    }




    @Override
    public List<Course> GetGyTypeandMajor(String courseType, String major) {
        return courseMapper.GetGyTypeandMajor(courseType, major);
    }



}
