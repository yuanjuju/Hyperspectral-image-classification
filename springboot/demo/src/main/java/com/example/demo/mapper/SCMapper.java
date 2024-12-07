package com.example.demo.mapper;

import com.example.demo.pojo.SC;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface SCMapper {
    @Select("select Cno from sc where Sno=#{sno}")
    List<String> getbysno(String sno);

    @Insert("insert into sc(Sno, Cno,name,credit,semester) values (#{sno},#{courseId},#{coursename},#{coursecredit},#{coursesemester})")
    void insert(String sno, String courseId,String coursename,Integer coursecredit,String coursesemester);

    @Delete("delete from sc where Sno=#{sno} and Cno=#{courseId}")
    void delete(String sno, String courseId);

    @Select("select * from sc where Sno=#{sno}")
    List<SC> getallmark(String sno);


    @Select("select * from sc where Sno=#{sno} and semester=#{semester}")
    List<SC> getpartmark(String sno, String semester);
}
