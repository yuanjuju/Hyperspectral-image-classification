package com.example.demo.controller;

import com.example.demo.pojo.Result;
import com.example.demo.pojo.SC;
import com.example.demo.service.SCSerivice;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Objects;

@RestController
@RequestMapping("/api")
public class ScController {
    @Autowired
    private SCSerivice scSerivice;

    @GetMapping("/selectCourse")
    public Result selectCourse(String sno ,String courseId,String coursename,Integer coursecredit,String coursesemester) {
        scSerivice.insert(sno,courseId,coursename,coursecredit,coursesemester);
        return Result.success();

    }

    @GetMapping("/deleteCourse")
    public Result deleteCourse(String sno,String courseId) {
        scSerivice.deleteCourse(sno,courseId);
        return Result.success();
    }

    @GetMapping("/allcourse")
    public Result allCourse(String sno,String semester) {
        System.out.println(sno);
        System.out.println(semester);
        if(Objects.equals(semester, "入学以来"))
        {
            List<SC> scList=scSerivice.getallmark(sno);
            System.out.println(sno);
            System.out.println(scList);
            return Result.success(scList);
        }
        else
        {
            List<SC> scList=scSerivice.getpartmark(sno,semester);
            return Result.success(scList);
        }

    }

}
