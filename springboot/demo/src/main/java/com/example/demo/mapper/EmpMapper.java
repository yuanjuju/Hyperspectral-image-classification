package com.example.demo.mapper;

import com.example.demo.pojo.Emp;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface EmpMapper {


    List<Emp> list(String name, Short gender, LocalDateTime begin, LocalDateTime end);

    void delete(List<Integer> ids);

    @Select("select * from emp where username=#{username} and password=#{password}")
    Emp getByUsernameAndPassword(Emp emp);
}
