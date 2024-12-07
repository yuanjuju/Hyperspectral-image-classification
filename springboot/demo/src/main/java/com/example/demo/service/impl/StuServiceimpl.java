package com.example.demo.service.impl;


import com.example.demo.mapper.StuMapper;
import com.example.demo.pojo.Student;
import com.example.demo.service.StuService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class StuServiceimpl implements StuService {
    @Autowired
    private StuMapper stuMapper;
    @Override
    public Student login(String sno, String password) {
        return stuMapper.getBysnoAndPassword(sno,password);
    }
    @Override
    public Student studentInfo(String Sno)
    {
        return stuMapper.getBysno(Sno);
    }
    @Override
    public Student getbyphone(String phone)
    {
        return stuMapper.getbyphone(phone);
    }

    @Override
    public void resetpassword(String phone, String newPassword)
    {
        stuMapper.resetpassword(phone,newPassword);
    }
    @Override
    public Student getbypassword(String oldPassword)
    {
        return stuMapper.getbypassword(oldPassword);
    }
    @Override
    public void changepassword(String oldPassword, String newPassword)
    {
         stuMapper.changepassword(oldPassword,newPassword);
    }

    @Override
    public void modifyinformation(Student student)
    {
        stuMapper.modifyinformation(student);
    }


    @Override
    public void softinsert(String sno, String newPhone, String newPassword)
    {
        stuMapper.softinsert(sno,newPhone,newPassword);
    }



}
