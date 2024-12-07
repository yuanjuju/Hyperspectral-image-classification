package com.example.demo.controller;

import com.example.demo.pojo.Course;
import com.example.demo.pojo.Result;
import com.example.demo.service.CourseService;
import com.example.demo.service.SCSerivice;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api")
public class CourseController {
    @Autowired
    private CourseService courseService;

    @Autowired
    private SCSerivice scSerivice;

    @GetMapping("/courseInfo")
    public Result courseInfo() {
        List<Course> courseList=courseService.getcourseinfo();
        System.out.println(courseList);
        return Result.success(courseList);
    }

    @GetMapping("/courses")
    public Result Course(@RequestParam("sno") String sno) {

        List<String> conlist=scSerivice.getbysno(sno);


        List<Course> courseList = new ArrayList<>();

        // 遍历 conlist 中的每个 cno，调用 courseService.getbycno() 查询
        for (String cno : conlist) {
            try {
                Course course = courseService.getbycno(cno);
                if (course != null) {
                    courseList.add(course);
                } else {
                    System.out.println("未找到课程编号为 " + cno + " 的课程信息");
                }
            } catch (Exception e) {
                System.err.println("查询课程编号为 " + cno + " 时出错: " + e.getMessage());
            }
        }
        return Result.success(courseList);
    }


    @GetMapping("/searchCourses")
    public Result searchCourses(String courseType, String major) {

        List<Course> courseList = courseService.GetGyTypeandMajor(courseType,major);
        return Result.success(courseList);

    }


}
