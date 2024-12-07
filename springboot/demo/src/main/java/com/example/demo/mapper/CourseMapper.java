package com.example.demo.mapper;

import com.example.demo.pojo.Course;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface CourseMapper {
    @Select("select * from course where Ccno=#{cno}")
    Course getbycno(String cno);


    @Select("select * from course")
    List<Course> getcourseinfo();

    @Select("select * from course where Cclass=#{courseType} and Cprofession=#{major}")
    List<Course> GetGyTypeandMajor(String courseType, String major);
}
