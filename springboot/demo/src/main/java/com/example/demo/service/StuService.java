package com.example.demo.service;


import com.example.demo.pojo.Student;

public interface StuService {
    Student login(String sno, String password);

    Student studentInfo(String sno);

    Student getbyphone(String phone);


    void resetpassword(String phone, String newPassword);

    Student getbypassword(String oldPassword);

    void changepassword(String oldPassword, String newPassword);

    void modifyinformation(Student student);

    void softinsert(String sno, String newPhone, String newPassword);
}
