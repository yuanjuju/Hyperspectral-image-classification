package com.example.demo.controller;


import com.example.demo.pojo.ChangePasswordBean;
import com.example.demo.pojo.Result;
import com.example.demo.pojo.Student;
import com.example.demo.service.StuService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class StudentController {
    @Autowired
    private StuService stuService;
    @GetMapping("/student-info")
    public Result studentInfo(String Sno) {
        System.out.println(Sno);
        System.out.println(stuService.studentInfo(Sno));
        Student student = stuService.studentInfo(Sno);
        return  Result.success(student);

    }
    @PostMapping("/change-password")
    public Result change(@RequestBody ChangePasswordBean changePasswordBean) {
        String oldPassword = changePasswordBean.getOldPassword();
        String newPassword = changePasswordBean.getNewPassword();
        Student s = stuService.getbypassword(oldPassword);
        if(s!= null)
        {
            stuService.changepassword(oldPassword,newPassword);
        }
        return Result.success();
    }
    @PostMapping("/save-student-info")
    public Result saveStudentInfo(@RequestBody Student student) {
        stuService.modifyinformation(student);
        return Result.success();
    }
}
