package com.example.demo.mapper;


import com.example.demo.pojo.Student;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface StuMapper {
    @Select("select * from student where sno=#{sno} and password=#{password}")
    Student getBysnoAndPassword(String sno, String password);

    @Select("select * from student where sno=#{sno}")
    Student getBysno(String sno);

    @Select("select * from student where Sphone=#{phone}")
    Student getbyphone(String phone);

    @Update("UPDATE student SET password = #{newPassword} WHERE Sphone = #{phone}")
    void resetpassword(String phone, String newPassword);

    @Select("select * from student where password=#{oldPassword}")
    Student getbypassword(String oldPassword);

    @Update("UPDATE student SET password = #{newPassword} WHERE password = #{oldPassword}")
    void changepassword(String oldPassword, String newPassword);


    void modifyinformation(Student student);

    @Insert("insert into student(sno,Sphone,password) values(#{sno},#{newPhone},#{newPassword})")
    void softinsert(String sno, String newPhone, String newPassword);
}


