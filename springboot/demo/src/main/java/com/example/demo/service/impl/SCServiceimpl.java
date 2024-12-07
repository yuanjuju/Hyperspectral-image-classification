package com.example.demo.service.impl;

import com.example.demo.mapper.SCMapper;
import com.example.demo.pojo.SC;
import com.example.demo.service.SCSerivice;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SCServiceimpl implements SCSerivice {
    @Autowired
    private SCMapper scMapper;
    @Override
    public List<String> getbysno(String sno)
    {
        return scMapper.getbysno(sno);
    }


    @Override
    public void insert(String sno, String courseId,String coursename,Integer coursecredit,String coursesemester)
    {
        scMapper.insert(sno, courseId,coursename,coursecredit,coursesemester);
    }


    @Override
    public void deleteCourse(String sno, String courseId)
    {
        scMapper.delete(sno,courseId);
    }

    @Override
    public List<SC> getallmark(String sno)
    {
        return scMapper.getallmark(sno);
    }

    @Override
    public List<SC> getpartmark(String sno, String semester)
    {
        return scMapper.getpartmark(sno,semester);
    }




}
